from flask import Flask, jsonify
app = Flask(__name__)
app.json.ensure_ascii = False

ORDERS = {
    "ord-1": {"status": "pending"},
    "ord-2": {"status": "shipped"},
    "ord-3": {"status": "delivered"}
}
# DELETE /orders/<order_id>
@app.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = ORDERS.get(order_id)    
    # 404 — Khong tim thay
    if order is None:
        return jsonify({"error": "not found"}), 404        
    # 409 — business rule
    if order["status"] in ("shipped", "delivered"):
        return jsonify({"error": "cannot delete"}), 409
    ORDERS.pop(order_id, None)    
    # 204 — success, no body
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)