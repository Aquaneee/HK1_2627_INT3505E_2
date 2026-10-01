import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

# Danh sách dữ liệu mẫu
ORDERS = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 150.0},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 80.5},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 220.0},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 45.0},
    {"id": 5, "customer_id": 102, "status": "paid", "total": 310.0},
    {"id": 6, "customer_id": 101, "status": "paid", "total": 95.0},
]

@app.route("/orders", methods=["GET"])
def get_orders():
    # 1. Cursor: giải mã base64 chứa ID cuối cùng của trang trước
    cursor_id = None
    cursor_param = request.args.get("cursor")
    if cursor_param:
        try:
            cursor_id = int(base64.b64decode(cursor_param).decode("utf-8"))
        except Exception:
            # Cursor hỏng trả về 400
            return jsonify({"error": "Invalid cursor"}), 400

    # Lấy các tham số lọc và phân trang
    status = request.args.get("status")
    customer_id = request.args.get("customer_id")
    sort_by = request.args.get("sort", "id")
    fields = request.args.get("fields")
    limit = int(request.args.get("limit", 10))

    # 2. Filter: lọc theo status và customer_id
    data = ORDERS
    if status:
        data = [item for item in data if item["status"] == status]
    if customer_id:
        data = [item for item in data if item["customer_id"] == int(customer_id)]

    # 3. Sort: sắp xếp danh sách theo trường yêu cầu
    if sort_by in ["id", "total", "status", "customer_id"]:
        data = sorted(data, key=lambda x: x[sort_by])

    # 4. Phân trang cursor: chỉ lấy các bản ghi có id lớn hơn cursor_id
    if cursor_id is not None:
        data = [item for item in data if item["id"] > cursor_id]

    # Cắt theo limit
    paged_data = data[:limit]

    # Tạo next_cursor nếu còn dữ liệu tiếp theo
    next_cursor = None
    if len(paged_data) > 0 and len(data) > limit:
        last_id = str(paged_data[-1]["id"])
        next_cursor = base64.b64encode(last_id.encode("utf-8")).decode("utf-8")

    # 5. Sparse fieldsets: lọc trường cần lấy
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result = [
            {k: item[k] for k in field_list if k in item}
            for item in paged_data
        ]
    else:
        result = paged_data

    return jsonify({
        "data": result,
        "next_cursor": next_cursor
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)