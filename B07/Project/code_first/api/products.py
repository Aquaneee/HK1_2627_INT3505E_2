from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ProductSchema, ProductInSchema

# Giả lập database
mock_db = [
    {"id": 1, "name": "Laptop", "price": 1200.0},
    {"id": 2, "name": "Mouse", "price": 25.0}
]

blp = Blueprint("products", __name__, url_prefix="/products", description="Product operations")

@blp.route("")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return mock_db

    @blp.arguments(ProductInSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        new_id = max([p["id"] for p in mock_db], default=0) + 1
        new_product = {"id": new_id, **data}
        mock_db.append(new_product)
        return new_product

@blp.route("/<int:id>")
class ProductDetail(MethodView):
    @blp.response(200, ProductSchema)
    def get(self, id):
        product = next((p for p in mock_db if p["id"] == id), None)
        if product is None:
            abort(404, message="Product not found")
        return product