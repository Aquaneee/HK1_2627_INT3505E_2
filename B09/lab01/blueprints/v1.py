from flask import Blueprint
from .users_data import get_user

bp = Blueprint("v1", __name__, url_prefix="/users")

@bp.after_request
def add_sunset_header(response):
    # Thông báo thời điểm v1 ngừng hoạt động (định dạng HTTP-date)
    response.headers["Sunset"] = "Wed, 31 Dec 2026 23:59:59 GMT"
    response.headers["Deprecation"] = "true"
    return response

@bp.route("/<int:uid>", methods=["GET"])
def get(uid):
    u = get_user(uid)
    if not u:
        return {"error": "nf"}, 404
    return {
        "id": uid,
        "full_name": f"{u['first_name']} {u['last_name']}",
        "email": u["email"]
    }