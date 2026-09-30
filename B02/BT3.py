import hashlib
import json
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

BOOKS = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "price": 30.0,
    }
]


def generate_etag(data: dict) -> str:
    content = json.dumps(data, sort_keys=True)
    digest = hashlib.md5(content.encode("utf-8")).hexdigest()
    return f'"{digest}"'


@app.get("/books/<int:bid>")
def get_book_by_id(bid):
    # 1. Tìm sách theo ID
    book = next((b for b in BOOKS if b["id"] == bid), None)
    if book is None:
        return jsonify(error="not found"), 404
    # 2. Sinh mã ETag theo nội dung hiện tại của bản ghi
    etag = generate_etag(book)
    # 3. Kiểm tra header điều kiện If-None-Match từ request của client
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match and if_none_match.strip() == etag:
        # Dữ liệu không thay đổi -> trả về 304 Not Modified, body rỗng
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "public, max-age=60"
        return resp
    # 4. Lần đầu gọi hoặc dữ liệu có thay đổi -> trả 200 OK kèm payload và header ETag
    resp = make_response(jsonify(book), 200)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "public, max-age=60"
    return resp

if __name__ == "__main__":
    app.run(debug=True)