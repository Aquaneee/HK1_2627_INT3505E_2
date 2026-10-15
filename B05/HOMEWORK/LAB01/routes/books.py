import base64
import json
import os
from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from sqlalchemy import asc, desc

from models import Book, Category, db

books_bp = Blueprint("books", __name__)

# Đọc JSON schema để validate khi tạo sách
schema_path = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "book.json"
)
if os.path.exists(schema_path):
    with open(schema_path, "r", encoding="utf-8") as f:
        book_schema = json.load(f)
else:
    book_schema = {}


def encode_cursor(val) -> str:
    """Mã hóa giá trị cursor sang base64."""
    return base64.b64encode(str(val).encode("utf-8")).decode("utf-8")


def decode_cursor(token: str) -> int:
    """Giải mã cursor token base64 thành integer id."""
    try:
        return int(base64.b64decode(token.encode("utf-8")).decode("utf-8"))
    except Exception:
        return None


def apply_sorting(query, sort_param: str):
    """
    Xử lý sắp xếp đa trường (Multi-key sort).
    Hỗ trợ các định dạng:
      - 'price_vnd:asc,id:desc'
      - 'price_vnd,-id' (dấu '-' đại diện cho desc)
    """
    sort_fields = {
        "id": Book.id,
        "title": Book.title,
        "isbn": Book.isbn,
        "price_vnd": Book.price_vnd,
        "stock": Book.stock,
    }

    if not sort_param:
        return query.order_by(Book.id.asc())

    clauses = []
    items = [item.strip() for item in sort_param.split(",") if item.strip()]
    for item in items:
        if ":" in item:
            field_name, order = item.split(":", 1)
            order = order.lower()
        elif item.startswith("-"):
            field_name = item[1:]
            order = "desc"
        else:
            field_name = item
            order = "asc"

        column = sort_fields.get(field_name)
        if column is not None:
            clauses.append(desc(column) if order == "desc" else asc(column))

    if clauses:
        return query.order_by(*clauses)
    return query.order_by(Book.id.asc())


@books_bp.route("/books", methods=["GET"])
def list_books():
    strategy = request.args.get("strategy", "offset").lower()
    genre = request.args.get("genre")
    sort_param = request.args.get("sort")

    # Base query
    query = Book.query

    # 1. Filter theo genre (Category name hoặc slug)
    if genre:
        query = query.join(Book.category).filter(
            (Category.name.ilike(f"%{genre}%")) | (Category.slug == genre)
        )

    # 2. Xử lý theo Strategy phân trang
    if strategy == "cursor":
        limit = request.args.get("limit", default=10, type=int)
        cursor = request.args.get("cursor")

        # Với cursor pagination cơ bản, ta sắp xếp theo id tăng dần
        query = query.order_by(Book.id.asc())

        if cursor:
            cursor_id = decode_cursor(cursor)
            if cursor_id is not None:
                query = query.filter(Book.id > cursor_id)

        # Lấy dư 1 item để kiểm tra xem còn trang tiếp theo hay không
        books = query.limit(limit + 1).all()
        has_more = len(books) > limit
        items = books[:limit]

        next_cursor = None
        if has_more and items:
            next_cursor = encode_cursor(items[-1].id)

        return jsonify({
            "strategy": "cursor",
            "data": [b.to_dict() for b in items],
            "limit": limit,
            "next_cursor": next_cursor,
            "has_more": has_more,
        }), 200

    else:
        # Strategy: Offset pagination (mặc định)
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=10, type=int)
        if page < 1:
            page = 1
        if limit < 1:
            limit = 10

        query = apply_sorting(query, sort_param)
        total_items = query.count()
        total_pages = (total_items + limit - 1) // limit

        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()

        return jsonify({
            "strategy": "offset",
            "data": [b.to_dict() for b in items],
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages,
            },
        }), 200


@books_bp.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Payload không hợp lệ"}), 400

    if book_schema:
        try:
            validate(instance=data, schema=book_schema)
        except ValidationError as err:
            return jsonify({"error": err.message}), 400

    if Book.query.filter_by(isbn=data["isbn"]).first():
        return jsonify({"error": "ISBN đã tồn tại"}), 409

    new_book = Book(
        title=data["title"],
        isbn=data["isbn"],
        price_vnd=data["price_vnd"],
        stock=data["stock"],
        category_id=data.get("category_id"),
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify(new_book.to_dict()), 201