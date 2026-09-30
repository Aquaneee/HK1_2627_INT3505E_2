import logging
import uuid
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

# URL gốc dùng để định danh lỗi
ERROR_BASE = "https://api.example.com/probs"


# ==========================================
# 1. errors.py
# ==========================================
class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        self.status = status
        self.title = title
        self.detail = detail
        self.type = f"{ERROR_BASE}/{type_path}" if type_path else "about:blank"
        self.extra = extra


def _problem(status, title, detail=None, type_path=None, **extra):
    body = {
        "type": f"{ERROR_BASE}/{type_path}" if type_path else "about:blank",
        "title": title,
        "status": status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4()),
    }
    if detail:
        body["detail"] = detail
    body.update(extra)

    resp = jsonify(body)
    resp.status_code = status
    resp.headers["Content-Type"] = "application/problem+json"
    return resp


# ==========================================
# 2. ĐĂNG KÝ ERROR HANDLERS
# ==========================================
# Handler cho ApiProblem tùy chỉnh
@app.errorhandler(ApiProblem)
def handle_api_problem(error):
    # Truyền trực tiếp các thuộc tính đã gán trong ApiProblem
    return _problem(
        status=error.status,
        title=error.title,
        detail=error.detail,
        type_path=None,  # Đã được định dạng sẵn trong error.type
        **{"type": error.type, **error.extra},
    )


# Handler fallback cho HTTPException (404, 405,...) của Flask/Werkzeug
@app.errorhandler(HTTPException)
def handle_http_exception(error):
    return _problem(
        status=error.code,
        title=error.name,
        detail=error.description,
        type_path=None,
    )


# Handler cho các Exception chưa bắt (500 Internal Server Error)
@app.errorhandler(Exception)
def handle_unexpected_exception(error):
    # Log chi tiết phía server-side kèm stack trace
    app.logger.exception("Internal Server Error: %s", error)

    # Trả về message trung tính, không lộ thông tin code
    return _problem(
        status=500,
        title="Internal Server Error",
        detail="Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.",
        type_path="internal-server-error",
    )


# ==========================================
# 3. DÙNG TRONG ROUTE (Endpoint kiểm thử)
# ==========================================
@app.get("/users/<int:id>")
def get_user(id):
    # Giả lập tìm kiếm user trong database
    # Ví dụ chỉ có user id=42 tồn tại
    if id != 42:
        raise ApiProblem(
            status=404,
            title="User not found",
            type_path="user-not-found",
            resource_id=id,
        )

    return jsonify({"id": 42, "name": "Nguyen Van A"})


if __name__ == "__main__":
    app.run(debug=False)