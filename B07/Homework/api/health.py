from flask import Blueprint, jsonify
from sqlalchemy import text
from extensions import db

health_bp = Blueprint("health", __name__)

@health_bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

@health_bp.get("/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ready", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "not ready", "reason": str(e)}), 503