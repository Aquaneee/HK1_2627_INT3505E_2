# Giả lập database đơn giản để chạy độc lập
mock_db = [
    {"id": 1, "name": "Laptop", "price": 1200.0},
    {"id": 2, "name": "Mouse", "price": 25.0}
]

def list_products():
    return mock_db, 200

def create_product(body):
    new_id = max([p["id"] for p in mock_db], default=0) + 1
    new_product = {"id": new_id, **body}
    mock_db.append(new_product)
    return new_product, 201

def get_product(id):
    product = next((p for p in mock_db if p["id"] == id), None)
    if product is None:
        return {"message": "Not Found"}, 404
    return product, 200