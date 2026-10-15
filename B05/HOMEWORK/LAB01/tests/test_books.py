import pytest
from app import create_app
from models import Book, Category, db


@pytest.fixture
def client():
    # Khởi tạo app dùng database in-memory cho môi trường test
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Tạo category mẫu
            cat_it = Category(name="Information Technology", slug="it")
            cat_sci = Category(name="Science", slug="science")
            db.session.add_all([cat_it, cat_sci])
            db.session.commit()

            # Tạo dữ liệu mẫu 5 cuốn sách để test phân trang và filter
            books = [
                Book(
                    title="Flask Web Development",
                    isbn="978-0111111111",
                    price_vnd=200000,
                    stock=10,
                    category=cat_it,
                ),
                Book(
                    title="Python Crash Course",
                    isbn="978-0222222222",
                    price_vnd=150000,
                    stock=25,
                    category=cat_it,
                ),
                Book(
                    title="A Brief History of Time",
                    isbn="978-0333333333",
                    price_vnd=180000,
                    stock=12,
                    category=cat_sci,
                ),
                Book(
                    title="Astrophysics for People in a Hurry",
                    isbn="978-0444444444",
                    price_vnd=90000,
                    stock=30,
                    category=cat_sci,
                ),
                Book(
                    title="Clean Code",
                    isbn="978-0555555555",
                    price_vnd=250000,
                    stock=5,
                    category=cat_it,
                ),
            ]
            db.session.add_all(books)
            db.session.commit()

        yield client

        # Dọn dẹp database sau khi chạy xong test
        with app.app_context():
            db.session.remove()
            db.drop_all()


def test_create_book_success(client):
    """Test POST tạo mới một cuốn sách hợp lệ."""
    payload = {
        "title": "Introduction to Algorithms",
        "isbn": "978-0262033848",
        "price_vnd": 300000,
        "stock": 15,
    }
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == payload["title"]
    assert "book_" in data["id"]


def test_create_book_duplicate_isbn(client):
    """Test POST với ISBN đã tồn tại thì phải trả về lỗi 409."""
    payload = {
        "title": "Duplicate Book",
        "isbn": "978-0111111111",  # Đã có trong seed data
        "price_vnd": 100000,
        "stock": 10,
    }
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 409


def test_offset_pagination(client):
    """Test phân trang kiểu Offset."""
    # Lấy trang 1, limit 2
    res = client.get("/api/v1/books?strategy=offset&page=1&limit=2")
    assert res.status_code == 200
    data = res.get_json()
    assert data["strategy"] == "offset"
    assert len(data["data"]) == 2
    assert data["pagination"]["total_items"] == 5
    assert data["pagination"]["total_pages"] == 3


def test_cursor_pagination(client):
    """Test phân trang kiểu Cursor."""
    # Lấy 2 cuốn đầu tiên
    res1 = client.get("/api/v1/books?strategy=cursor&limit=2")
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert len(data1["data"]) == 2
    assert data1["has_more"] is True
    assert data1["next_cursor"] is not None

    # Lấy trang tiếp theo dùng token next_cursor
    next_cursor = data1["next_cursor"]
    res2 = client.get(
        f"/api/v1/books?strategy=cursor&limit=2&cursor={next_cursor}"
    )
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert len(data2["data"]) == 2
    # Đảm bảo phần tử đầu trang 2 không trùng phần tử cuối trang 1
    assert data2["data"][0]["id"] != data1["data"][-1]["id"]


def test_filter_by_genre(client):
    """Test lọc theo genre (slug hoặc tên category)."""
    res = client.get("/api/v1/books?strategy=offset&genre=science")
    assert res.status_code == 200
    data = res.get_json()
    # Trong seed có 2 cuốn thuộc category Science
    assert len(data["data"]) == 2
    for b in data["data"]:
        assert b["category"]["slug"] == "science"


def test_multi_key_sort(client):
    """Test sắp xếp đa trường (ví dụ price_vnd giảm dần)."""
    res = client.get(
        "/api/v1/books?strategy=offset&sort=price_vnd:desc,id:asc"
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    # Giá cao nhất là Clean Code (250000)
    assert data[0]["title"] == "Clean Code"
    assert data[0]["price_vnd"] >= data[1]["price_vnd"]