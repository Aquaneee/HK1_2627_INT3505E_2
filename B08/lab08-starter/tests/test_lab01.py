import pytest

# ===========================================================================
# 4 TEST BẮT BUỘC (Sử dụng trực tiếp fixture 'client' có sẵn trong conftest.py)
# ===========================================================================

def test_get_books_empty_db(client):
    """A. GET /books khi CSDL rỗng trả về mảng rỗng (không phải null)."""
    response = client.get('/books')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0
    assert data is not None


def test_get_book_not_found(client):
    """B. GET /books/<id> với id không tồn tại trả về 404 + JSON chứa "code": "NOT_FOUND"."""
    response = client.get('/books/999999')
    assert response.status_code == 404
    
    data = response.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == "NOT_FOUND"


def test_post_book_missing_title(client):
    """C. POST /books thiếu title trả về 400 + trong errors có field "title"."""
    payload = {"author": "Unknown Author"}
    response = client.post('/books', json=payload)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    
    errors = data["errors"]
    if isinstance(errors, dict):
        assert "title" in errors
    elif isinstance(errors, list):
        assert any("title" in str(err) for err in errors)


def test_delete_then_get_book(client):
    """D. Xoá rồi GET cùng id — phải trả về 404."""
    create_resp = client.post('/books', json={"title": "Clean Code", "author": "Robert C. Martin"})
    assert create_resp.status_code in (200, 201)
    book_id = create_resp.get_json()["id"]

    delete_resp = client.delete(f'/books/{book_id}')
    assert delete_resp.status_code in (200, 204)

    get_resp = client.get(f'/books/{book_id}')
    assert get_resp.status_code == 404