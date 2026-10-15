import json
import os
from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from models import Book, db

books_bp = Blueprint("books", __name__)

# Đọc file schema để validate request body
schema_path = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "book.json"
)
with open(schema_path, "r", encoding="utf-8") as f:
    book_schema = json.load(f)


# GET /api/v1/books - Lấy danh sách tất cả sách
@books_bp.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200


# POST /api/v1/books - Tạo sách mới
@books_bp.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dữ liệu JSON không hợp lệ"}), 400

    try:
        validate(instance=data, schema=book_schema)
    except ValidationError as err:
        return jsonify({"error": err.message}), 400

    # Kiểm tra trùng ISBN
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