from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload
from extensions import db
from models.product import Product
from models.order import Order, OrderItem
from schemas import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.json)
    order = Order()
    db.session.add(order)

    for item_data in body["items"]:
        product = db.get_or_404(Product, item_data["product_id"])
        if product.archived or product.qty_in_stock < item_data["quantity"]:
            db.session.rollback()
            return jsonify({"error": "Product unavailable or insufficient stock"}), 400

        product.qty_in_stock -= item_data["quantity"]
        order_item = OrderItem(
            product_id=product.id,
            quantity=item_data["quantity"],
            price_cents=product.price_cents
        )
        order.items.append(order_item)

    db.session.commit()
    return OrderOut().dump(order), 201

@orders_bp.get("")
def list_orders():
    stmt = db.select(Order).options(selectinload(Order.items)).order_by(Order.id.desc())
    orders = db.session.scalars(stmt).all()
    return jsonify(OrderOut(many=True).dump(orders)), 200