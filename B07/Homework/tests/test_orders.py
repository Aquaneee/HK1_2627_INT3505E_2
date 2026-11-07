import pytest
from sqlalchemy import event
from extensions import db
from models.product import Product
from models.order import Order, OrderItem

def test_create_order(client):
    product = Product(sku="SKU001", name="Test Product", price_cents=1000, qty_in_stock=10)
    db.session.add(product)
    db.session.commit()

    payload = {
        "items": [
            {"product_id": product.id, "quantity": 2}
        ]
    }
    response = client.post("/api/v1/orders", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2

def test_list_orders_n_plus_one_prevention(client):
    for i in range(3):
        prod = Product(sku=f"SKU00{i}", name=f"Prod {i}", price_cents=500, qty_in_stock=5)
        db.session.add(prod)
        db.session.commit()

        order = Order()
        order.items.append(OrderItem(product_id=prod.id, quantity=1, price_cents=500))
        db.session.add(order)
        db.session.commit()

    queries_executed = 0

    def before_cursor_execute(conn, cursor, statement, parameters, context, execmany):
        nonlocal queries_executed
        queries_executed += 1

    event.listen(db.engine, "before_cursor_execute", before_cursor_execute)

    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    assert len(response.get_json()) == 3

    # Dùng selectinload nên số query tối đa là 2 (1 fetch orders, 1 fetch order_items IN (...))
    assert queries_executed <= 2, f"N+1 query detected! Total queries: {queries_executed}"

    event.remove(db.engine, "before_cursor_execute", before_cursor_execute)