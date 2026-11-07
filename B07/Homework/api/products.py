from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.product import Product
from errors import Conflict
from schemas import (
    ProductOut, ProductIn, ProductPatch, ReserveIn
)

products_bp = Blueprint(
    "products", __name__, url_prefix="/api/v1/products"
)

# 1. GET /api/v1/products - Danh sách phân trang
@products_bp.get("")
def list_products():
    page = max(1, int(request.args.get("page", 1)))
    size = min(100, max(1, int(request.args.get("size", 20))))

    base = db.select(Product).where(Product.archived.is_(False))
    rows = db.session.execute(
        base.order_by(Product.id)
        .offset((page - 1) * size)
        .limit(size)
    ).scalars().all()

    total = db.session.scalar(
        db.select(db.func.count()).select_from(Product)
        .where(Product.archived.is_(False))
    )

    return jsonify({
        "items": [ProductOut().dump(p) for p in rows],
        "page": page,
        "size": size,
        "total": total
    }), 200

# 2. GET /api/v1/products/<int:id> - Lấy 1 sản phẩm
@products_bp.get("/<int:id>")
def get_product(id: int):
    p = db.get_or_404(Product, id)
    if p.archived:
        db.abort(404)
    return ProductOut().dump(p), 200

# 3. POST /api/v1/products - Tạo sản phẩm
@products_bp.post("")
def create_product():
    body = ProductIn().load(request.json)
    p = Product(**body)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict(message="sku already exists")
    return ProductOut().dump(p), 201

# 4. POST /api/v1/products/<int:id>/reserve - Đặt trước sản phẩm
@products_bp.post("/<int:id>/reserve")
def reserve_product(id: int):
    p = db.get_or_404(Product, id)
    if p.archived:
        db.abort(404)

    body = ReserveIn().load(request.json)
    reserve_qty = body["qty"]

    if p.qty_in_stock < reserve_qty:
        raise Conflict(message="Not enough stock available")

    p.qty_in_stock -= reserve_qty
    db.session.commit()
    return ProductOut().dump(p), 200

# 5. PATCH /api/v1/products/<int:id> - Cập nhật một phần
@products_bp.patch("/<int:id>")
def patch_product(id: int):
    body = ProductPatch().load(request.json, partial=True)
    p = db.get_or_404(Product, id)
    if p.archived:
        db.abort(404)

    for k, v in body.items():
        setattr(p, k, v)
    db.session.commit()
    return ProductOut().dump(p), 200

# 6. DELETE /api/v1/products/<int:id> - Soft delete
@products_bp.delete("/<int:id>")
def delete_product(id: int):
    p = db.get_or_404(Product, id)
    p.archived = True
    db.session.commit()
    return "", 204