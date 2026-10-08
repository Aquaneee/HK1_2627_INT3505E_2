import base64
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

ORDERS = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 150.0},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 80.5},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 220.0},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 45.0},
    {"id": 5, "customer_id": 102, "status": "paid", "total": 310.0},
    {"id": 6, "customer_id": 101, "status": "paid", "total": 95.0},
]

def encode_cursor(val, item_id):
    payload = json.dumps({"v": val, "id": item_id})
    return base64.b64encode(payload.encode("utf-8")).decode("utf-8")

def decode_cursor(cursor_str):
    try:
        data = json.loads(base64.b64decode(cursor_str.encode("utf-8")).decode("utf-8"))
        if "v" in data and "id" in data:
            return data["v"], data["id"]
        return None
    except Exception:
        return None

@app.route("/orders", methods=["GET"])
def get_orders():
    # 1. Parse params
    cursor_param = request.args.get("cursor")
    status = request.args.get("status")
    customer_id = request.args.get("customer_id")
    sort_by = request.args.get("sort", "id")
    fields = request.args.get("fields")
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({"error": "Invalid limit"}), 400

    # 2. Xử lý cursor lỗi -> 400
    cursor_info = None
    if cursor_param:
        cursor_info = decode_cursor(cursor_param)
        if not cursor_info:
            return jsonify({"error": "Invalid cursor format"}), 400

    # 3. Filter
    data = ORDERS
    if status:
        data = [item for item in data if item["status"] == status]
    if customer_id:
        try:
            cid = int(customer_id)
            data = [item for item in data if item["customer_id"] == cid]
        except ValueError:
            return jsonify({"error": "Invalid customer_id"}), 400

    # 4. Sort
    is_desc = sort_by.startswith("-")
    field = sort_by.lstrip("-")
    if field not in ["id", "total", "customer_id"]:
        field = "id"
        is_desc = False

    data = sorted(data, key=lambda x: (x[field], x["id"]), reverse=is_desc)

    # 5. Áp dụng Cursor + Sort
    if cursor_info:
        cur_v, cur_id = cursor_info
        if not is_desc:
            data = [x for x in data if (x[field], x["id"]) > (cur_v, cur_id)]
        else:
            data = [x for x in data if (x[field], x["id"]) < (cur_v, cur_id)]

    paged_data = data[:limit]

    # Tạo next_cursor
    next_cursor = None
    if len(data) > limit and paged_data:
        last_item = paged_data[-1]
        next_cursor = encode_cursor(last_item[field], last_item["id"])

    # 6. Sparse fieldsets
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result = [{k: item[k] for k in field_list if k in item} for item in paged_data]
    else:
        result = paged_data

    return jsonify({"data": result, "next_cursor": next_cursor})

if __name__ == "__main__":
    app.run(port=5000, debug=True)