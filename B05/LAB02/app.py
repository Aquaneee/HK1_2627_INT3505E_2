import base64
import json
from flask import Flask, jsonify, request
from sqlalchemy import Integer, String, create_engine, select, tuple_
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

app = Flask(__name__)
DB_URL = "sqlite:///books.db"
engine = create_engine(DB_URL, echo=False)


# --- 1. Model & Database Setup ---
class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)
    price_vnd: Mapped[int] = mapped_column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category_id": self.category_id,
            "price_vnd": self.price_vnd,
        }


Base.metadata.create_all(engine)


def seed_data():
    """Khởi tạo một số sách mẫu nếu bảng đang trống."""
    with Session(engine) as session:
        has_books = session.scalars(select(Book.id).limit(1)).first()
        if not has_books:
            sample_books = [
                Book(title="Clean Code", category_id=1, price_vnd=350000),
                Book(
                    title="The Pragmatic Programmer",
                    category_id=1,
                    price_vnd=300000,
                ),
                Book(
                    title="Design Patterns", category_id=1, price_vnd=250000
                ),
                Book(
                    title="Refactoring", category_id=1, price_vnd=250000
                ),  # Cùng giá để test tie-break id
                Book(
                    title="Database System Concepts",
                    category_id=2,
                    price_vnd=200000,
                ),
                Book(
                    title="Computer Networks",
                    category_id=2,
                    price_vnd=150000,
                ),
                Book(
                    title="Operating Systems",
                    category_id=2,
                    price_vnd=100000,
                ),
            ]
            session.add_all(sample_books)
            session.commit()


seed_data()


# --- 2. Whitelist & Helper Functions ---
SORT = {"id": Book.id, "price": Book.price_vnd}  #[cite: 1]


def parse_sort(raw: str):  #[cite: 1]
    desc = raw.startswith("-")  #[cite: 1]
    key = raw.lstrip("-")  #[cite: 1]
    if key not in SORT:  #[cite: 1]
        return None, "bad_sort", 400  #[cite: 1]

    p = SORT[key]  #[cite: 1]
    cols = [  #[cite: 1]
        p.desc() if desc else p.asc(),  #[cite: 1]
        Book.id.desc() if desc else Book.id.asc(),  #[cite: 1]
    ]  #[cite: 1]
    return p, cols, desc  #[cite: 1]


def _enc(s: dict) -> str:  #[cite: 2]
    return (
        base64.urlsafe_b64encode(json.dumps(s).encode())  #[cite: 2]
        .decode()  #[cite: 2]
        .rstrip("=")  #[cite: 2]
    )  #[cite: 2]


def apply_cursor(
    q, raw: str, sort: str, p, desc: bool
):  #[cite: 2]
    if not raw:  #[cite: 2]
        return q, None, 200  #[cite: 2]

    try:
        pad = "=" * (-len(raw) % 4)  #[cite: 2]
        c = json.loads(
            base64.urlsafe_b64decode(raw + pad)
        )  #[cite: 2]
    except Exception:
        return None, "invalid_cursor", 400

    if c.get("s") != sort:  #[cite: 2]
        return None, "sort_chg", 400  #[cite: 2]

    v, i = c.get("v"), c.get("i")  #[cite: 2]
    op = "<" if desc else ">"  #[cite: 2]
    condition = tuple_(p, Book.id).op(op)((v, i))  #[cite: 2]
    return q.filter(condition), None, 200  #[cite: 2]


def build_response(
    items: list, lim: int, sort: str, p, more: bool
):  #[cite: 2]
    nxt = None  #[cite: 2]
    if items and more:  #[cite: 2]
        last = items[-1]  #[cite: 2]
        nxt = _enc(
            {  #[cite: 2]
                "s": sort,  #[cite: 2]
                "v": getattr(last, p.key),  #[cite: 2]
                "i": last.id,  #[cite: 2]
            }
        )  #[cite: 2]

    return jsonify(  #[cite: 2]
        {  #[cite: 2]
            "data": [b.to_dict() for b in items],  #[cite: 2]
            "page": {"next": nxt, "more": more},  #[cite: 2]
        }
    )  #[cite: 2]


# --- 3. Route API ---
@app.get("/api/v1/books")
def list_books():  #
    raw_cursor = request.args.get("cursor")  #[cite: 3]
    lim = min(
        request.args.get("limit", 20, type=int), 100
    )  #[cite: 3]
    sort = request.args.get("sort", "-id")  #[cite: 3]
    cat = request.args.get("category", type=int)  #[cite: 3]

    p, cols, desc = parse_sort(sort)  #[cite: 3]
    if p is None:  #[cite: 3]
        return {"error": cols}, 400  #[cite: 3]

    q = select(Book).order_by(*cols)  #[cite: 3]
    if cat:  #[cite: 3]
        q = q.filter(Book.category_id == cat)  #[cite: 3]

    q, err, code = apply_cursor(
        q, raw_cursor, sort, p, desc
    )  #[cite: 3]
    if err:  #[cite: 3]
        return {"e": err}, code  #[cite: 3]

    with Session(engine) as session:
        rows = session.scalars(q.limit(lim + 1)).all()  #[cite: 3]
        has_more = len(rows) > lim  #[cite: 3]
        return build_response(
            rows[:lim], lim, sort, p, has_more
        )  #[cite: 3]


if __name__ == "__main__":
    app.run(debug=True, port=5000)