from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập dữ liệu trong bộ nhớ
posts = [
    {"id": 1, "title": "Bài viết đầu tiên", "content": "Nội dung bài 1", "author_id": 101, "tags": ["python", "api"]},
    {"id": 2, "title": "Học Flask RESTful", "content": "Nội dung bài 2", "author_id": 102, "tags": ["flask"]}
]

# 1. GET /api/v1/posts - Lấy danh sách bài viết (hỗ trợ lọc theo tag)
@app.route("/api/v1/posts", methods=["GET"])
def get_posts():
    tag = request.args.get("tag")
    if tag:
        filtered = [p for p in posts if tag in p.get("tags", [])]
        return jsonify(filtered), 200
    return jsonify(posts), 200

# 2. POST /api/v1/posts - Tạo bài viết mới
@app.route("/api/v1/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Thiếu dữ liệu tiêu đề hoặc nội dung"}), 400

    new_id = len(posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
        "author_id": data.get("author_id", 1),
        "tags": data.get("tags", [])
    }
    posts.append(new_post)
    return jsonify(new_post), 201

# 3. GET /api/v1/posts/<int:post_id> - Lấy chi tiết 1 bài viết
@app.route("/api/v1/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    return jsonify(post), 200

# 4. PUT /api/v1/posts/<int:post_id> - Cập nhật toàn bộ bài viết
@app.route("/api/v1/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    
    data = request.get_json()
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    post["tags"] = data.get("tags", post["tags"])
    return jsonify(post), 200

# 5. DELETE /api/v1/posts/<int:post_id> - Xóa bài viết
@app.route("/api/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    global posts
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    
    posts = [p for p in posts if p["id"] != post_id]
    return jsonify({"message": f"Bài viết {post_id} đã được xóa"}), 200

if __name__ == "__main__":
    app.run(debug=True)