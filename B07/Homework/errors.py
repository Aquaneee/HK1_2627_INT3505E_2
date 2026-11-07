from flask import jsonify

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, detail: str = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.detail = detail

class Conflict(APIError):
    def __init__(self, message: str = "Conflict", detail: str = None):
        super().__init__(message=message, status_code=409, detail=detail)

class BadRequest(APIError):
    def __init__(self, message: str = "Bad Request", detail: str = None):
        super().__init__(message=message, status_code=422, detail=detail)

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {"error": error.message}
        if error.detail:
            response["detail"] = error.detail
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(422)
    def handle_unprocessable_entity(error):
        return jsonify({"error": "Unprocessable entity", "detail": str(error)}), 422