from flask import Flask, jsonify, request
app = Flask(__name__)
app.json.ensure_ascii = False

BOOKS = [
    {"id": "b1", "t": "Lap trinh Python co ban"},
    {"id": "b2", "t": "Python nang cao va Flask API"},
    {"id": "b3", "t": "Kien truc Microservices"},
]

def find_by_id(book_id):
    for b in BOOKS:
        if b["id"] == book_id:
            return b
    return None

# --- CỘT 1: PATH PARAMS (Biến trong URL) ---

# /books/<id> - id la string
@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200
# Ep kieu int ngay tu URL
@app.route("/items/<int:item_id>")
def get_item(item_id):
    return jsonify({"id": item_id}), 200

# --- CỘT 2: QUERY STRING (Bộ lọc / Phân trang) ---

# /books?limit=10&offset=0&q=python
@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    
    # Lọc các cuốn sách có chứa từ khóa q trong tiêu đề (b["t"])
    items = [b for b in BOOKS if q in b["t"].lower()]
    
    # Giới hạn số lượng trả về theo limit
    items = items[:limit]
    
    return jsonify({"items": items}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)