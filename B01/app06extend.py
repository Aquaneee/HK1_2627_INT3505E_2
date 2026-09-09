from flask import Flask, jsonify, request
app = Flask(__name__)
app.json.ensure_ascii = False
_next = 3
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "R. Martin", "year": 2008},
    {
        "id": 2,
        "title": "The Pragmatic Programmer",
        "author": "Andy Hunt",
        "year": 1999,
    },
]
def find(bid):
    return next((b for b in BOOKS if b["id"] == bid), None)
# (a) Tìm kiếm ?q=... ; (b) Sắp xếp ?sort=title
@app.route("/books", methods=["GET"])
def list_books():
    res = list(BOOKS)
    # (a) Tìm kiếm theo query ?q=... (không phân biệt hoa/thường trong title hoặc author)
    q = request.args.get("q", "").strip().lower()
    if q:
        res = [
            b
            for b in res
            if q in b["title"].lower() or q in b["author"].lower()
        ]
    # (b) Sort theo trường chỉ định (hỗ trợ ?sort=title hoặc ?sort=year)
    sort_by = request.args.get("sort")
    if sort_by in ("title", "year", "author"):
        res = sorted(
            res,
            key=lambda x: (
                x[sort_by].lower()
                if isinstance(x[sort_by], str)
                else x[sort_by]
            ),
        )
    # Giới hạn số lượng (mặc định 100)
    n = int(request.args.get("limit", 100))
    return jsonify(res[:n]), 200
# DETAIL — GET /books/<int:bid>
@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)
    if not book:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200
# CREATE — POST /books
# (c) Bắt buộc field year là số >= 1900
@app.route("/books", methods=["POST"])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    t, a = body.get("title"), body.get("author")
    y = body.get("year")
    if not t or not a:
        return jsonify({"error": "need title+author"}), 400
    # Kiểm tra ràng buộc year
    if y is None or not isinstance(y, int) or y < 1900:
        return jsonify({"error": "year must be an integer >= 1900"}), 400
    book = {"id": _next, "title": t, "author": a, "year": y}
    _next += 1
    BOOKS.append(book)
    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}
# UPDATE — PUT, DELETE — DELETE
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return jsonify({"error": "not found"}), 404
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        # Nếu client cập nhật field year, kiểm tra tính hợp lệ
        if "year" in data:
            y = data["year"]
            if not isinstance(y, int) or y < 1900:
                return (
                    jsonify({"error": "year must be an integer >= 1900"}),
                    400,
                )
            book["year"] = y
        if "title" in data:
            book["title"] = data["title"]
        if "author" in data:
            book["author"] = data["author"]
        return jsonify(book), 200
    BOOKS.remove(book)
    return "", 204
    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)