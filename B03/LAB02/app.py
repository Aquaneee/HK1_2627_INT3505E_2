import logging
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)


# 1. Định nghĩa exception tùy chỉnh theo chuẩn RFC 7807
class ProblemError(Exception):
    def __init__(self, status=400, title=None, detail=None, type_=None, instance=None):
        super().__init__(detail)
        self.status = status
        self.title = title or "Bad Request"
        self.detail = detail
        self.type_ = type_ or "about:blank"
        self.instance = instance


# Hàm trợ giúp tạo response application/problem+json
def make_problem_response(status, title, detail, type_="about:blank", instance=None):
    payload = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance or request.path,
    }
    response = jsonify(payload)
    response.status_code = status
    response.content_type = "application/problem+json"
    return response


# 2. Handler cho custom ProblemError
@app.errorhandler(ProblemError)
def handle_problem_error(error):
    return make_problem_response(
        status=error.status,
        title=error.title,
        detail=error.detail,
        type_=error.type_,
        instance=error.instance,
    )


# 3. Fallback handler cho các HTTPException chuẩn của Werkzeug/Flask (ví dụ: 404, 405, 400)
@app.errorhandler(HTTPException)
def handle_http_exception(error):
    return make_problem_response(
        status=error.code,
        title=error.name,
        detail=error.description,
        type_="about:blank",
    )


# 4. Handler cho các exception chưa được bắt (500 Internal Server Error)
# Log chi tiết server-side, không lộ stack trace ra client
@app.errorhandler(Exception)
def handle_unexpected_exception(error):
    app.logger.exception("Đã xảy ra lỗi không xác định: %s", error)
    return make_problem_response(
        status=500,
        title="Internal Server Error",
        detail="Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.",
        type_="about:blank",
    )


# --- Endpoint kiểm thử ---
@app.route("/resources/<int:id>", methods=["GET"])
def get_resource(id):
    # Giả lập không tìm thấy tài nguyên
    if id != 1:
        raise ProblemError(
            status=404,
            title="Resource Not Found",
            detail=f"Tài nguyên với ID {id} không tồn tại.",
            type_="https://example.com/probs/not-found",
        )
    return jsonify({"id": 1, "name": "Mẫu tài nguyên"})


@app.route("/trigger-500", methods=["GET"])
def trigger_500():
    # Giả lập lỗi code nội bộ
    return 1 / 0


if __name__ == "__main__":
    app.run(debug=False)