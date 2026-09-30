import sqlite3
from flask import Flask, jsonify, request, make_response, g

app = Flask(__name__)
DATABASE = "app.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                price REAL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT NOT NULL,
                total REAL NOT NULL
            )
        """)
        # Dữ liệu mẫu ban đầu
        cursor = db.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            db.execute("""
                INSERT INTO books (title, author, isbn, price)
                VALUES ('Clean Code', 'Robert C. Martin', '978-0132350884', 30.0)
            """)
        cursor = db.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            db.execute("""
                INSERT INTO orders (id, status, total)
                VALUES (1, 'pending', 60.0)
            """)
        db.commit()

# --- 1. GET /books (Pagination + Filtering + HATEOAS)
@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
    except ValueError:
        return jsonify(error="page and size must be int"), 400

    page = max(page, 1)
    size = max(min(size, 100), 1)

    db = get_db()
    query = "SELECT * FROM books WHERE 1=1"
    params = []

    author = request.args.get("author")
    if author:
        query += " AND LOWER(author) = LOWER(?)"
        params.append(author)

    q = (request.args.get("q") or "").strip().lower()
    if q:
        query += " AND LOWER(title) LIKE ?"
        params.append(f"%{q}%")

    count_query = f"SELECT COUNT(*) FROM ({query})"
    total = db.execute(count_query, params).fetchone()[0]

    offset = (page - 1) * size
    query += " LIMIT ? OFFSET ?"
    params.extend([size, offset])

    rows = db.execute(query, params).fetchall()
    items = [dict(r) for r in rows]
    last = (total + size - 1) // size if total > 0 else 1

    def u(p):
        return f"/books?page={p}&size={size}"

    links = {
        "self": {"href": u(page)},
        "first": {"href": u(1)},
        "last": {"href": u(max(last, 1))},
    }
    if page > 1:
        links["prev"] = {"href": u(page - 1)}
    if offset + size < total:
        links["next"] = {"href": u(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": last,
        },
        "_links": links,
    }
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp

# --- 2. GET /books/<id>
@app.get("/books/<int:bid>")
def get_book(bid):
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    if not row:
        return jsonify(error="not found"), 404
    
    resp = make_response(jsonify(dict(row)), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    return resp

# --- 3. POST /books
@app.post("/books")
def create_book():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or "").strip()
    a = (p.get("author") or "").strip()
    if not t or not a:
        return jsonify(error="title and author required"), 422

    isbn = p.get("isbn")
    price = p.get("price")

    db = get_db()
    cursor = db.execute(
        "INSERT INTO books (title, author, isbn, price) VALUES (?, ?, ?, ?)",
        (t, a, isbn, price)
    )
    db.commit()
    new_id = cursor.lastrowid
    
    book = {"id": new_id, "title": t, "author": a, "isbn": isbn, "price": price}
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{new_id}"
    return resp

# --- 4. PUT /books/<id>
@app.put("/books/<int:bid>")
def put_book(bid):
    db = get_db()
    exists = db.execute("SELECT 1 FROM books WHERE id = ?", (bid,)).fetchone()
    if not exists:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    t, a = p.get("title"), p.get("author")
    if not t or not a:
        return jsonify(error="need title+author"), 422

    t, a = t.strip(), a.strip()
    isbn = p.get("isbn")
    price = p.get("price")

    db.execute(
        "UPDATE books SET title = ?, author = ?, isbn = ?, price = ? WHERE id = ?",
        (t, a, isbn, price, bid)
    )
    db.commit()
    return jsonify({"id": bid, "title": t, "author": a, "isbn": isbn, "price": price}), 200

# --- 5. PATCH /books/<id>
@app.patch("/books/<int:bid>")
def patch_book(bid):
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    if not row:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    if p.get("price") is not None and p.get("price") < 0:
        return jsonify(error="price must be positive"), 422

    current = dict(row)
    for field in ["title", "author", "isbn", "price"]:
        if field in p:
            current[field] = p[field].strip() if isinstance(p[field], str) else p[field]

    db.execute(
        "UPDATE books SET title = ?, author = ?, isbn = ?, price = ? WHERE id = ?",
        (current["title"], current["author"], current["isbn"], current["price"], bid)
    )
    db.commit()
    return jsonify(current), 200

# --- 6. DELETE /books/<id>
@app.delete("/books/<int:bid>")
def delete_book(bid):
    db = get_db()
    cursor = db.execute("DELETE FROM books WHERE id = ?", (bid,))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify(error="not found"), 404
    return "", 204

# --- 7. GET /orders/<oid> kèm HATEOAS
@app.get("/orders/<int:oid>")
def get_order(oid):
    db = get_db()
    row = db.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
    if not row:
        return jsonify(error="not found"), 404

    order = dict(row)
    order["_links"] = {
        "self": {"href": f"/orders/{oid}"},
        "cancel": {"href": f"/orders/{oid}/cancel", "method": "POST"}
    }
    return jsonify(order), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)