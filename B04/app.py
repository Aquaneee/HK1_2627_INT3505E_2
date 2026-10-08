import json
import yaml
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Đọc file spec openapi.yaml
def load_spec():
    with open('openapi.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Endpoint 1: Trả về file OpenAPI dạng JSON[cite: 27, 28, 34]
@app.route('/openapi.json', methods=['GET'])
def get_openapi_json():
    spec = load_spec()
    return jsonify(spec)

# Endpoint 2: Giao diện Swagger UI nhúng CDN tại /docs[cite: 27, 28, 34]
SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Swagger UI - Tasks API</title>
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
      });
    };
  </script>
</body>
</html>
"""

@app.route('/docs', methods=['GET'])
def render_swagger_ui():
    return render_template_string(SWAGGER_UI_HTML)

# --- Mock API Endpoints hỗ trợ nút "Try it out" ---

tasks_db = {
    "123e4567-e89b-12d3-a456-426614174000": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Hoàn thành bài tập OpenAPI",
        "status": "open",
        "priority": "high",
        "dueDate": "2026-10-15",
        "assigneeId": "usr_9988"
    }
}

@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    return jsonify([
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Hoàn thành bài tập OpenAPI",
            "status": "open",
            "priority": "high"
        }
    ]), 200

@app.route('/v1/tasks', methods=['POST'])
def create_task():
    import uuid
    new_id = str(uuid.uuid4())
    new_task = {
        "id": new_id,
        "title": "Task mới tạo",
        "status": "open",
        "priority": "normal"
    }
    tasks_db[new_id] = new_task
    return jsonify(new_task), 201

@app.route('/v1/tasks/<taskId>', methods=['GET'])
def get_task(taskId):
    task = tasks_db.get(taskId)
    if not task:
        return jsonify({"title": "Not Found", "status": 404, "detail": "Task không tồn tại"}), 404
    return jsonify(task), 200

@app.route('/v1/tasks/<taskId>', methods=['PATCH'])
def patch_task(taskId):
    task = tasks_db.get(taskId)
    if not task:
        return jsonify({"title": "Not Found", "status": 404, "detail": "Task không tồn tại"}), 404
    task["status"] = "done"
    return jsonify(task), 200

@app.route('/v1/tasks/<taskId>', methods=['DELETE'])
def delete_task(taskId):
    if taskId in tasks_db:
        del tasks_db[taskId]
    return '', 204

if __name__ == '__main__':
    app.run(port=5000, debug=True)