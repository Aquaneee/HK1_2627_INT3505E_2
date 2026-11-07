import connexion

# Khởi tạo app với thư mục chứa spec yaml
app = connexion.FlaskApp(__name__, specification_dir="openapi/")
app.add_api("products.yaml", validate_responses=True)

if __name__ == "__main__":
    # Swagger UI mặc định tại: http://localhost:5001/ui
    app.run(port=5001)