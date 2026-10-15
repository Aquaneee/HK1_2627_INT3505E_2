from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Bảng trung gian biểu diễn quan hệ nhiều - nhiều (N:M) giữa Book và Author
book_author = Table(
    "book_author",
    db.metadata,
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("author.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)

    # Quan hệ 1:N với Review
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": f"user_{self.id}",
            "email": self.email,
            "display_name": self.display_name,
        }


class Category(db.Model):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    # Quan hệ 1:N với Book
    books = relationship("Book", back_populates="category")

    def to_dict(self):
        return {
            "id": f"category_{self.id}",
            "name": self.name,
            "slug": self.slug,
        }


class Author(db.Model):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    bio = Column(String(500), nullable=True)

    # Quan hệ N:M với Book thông qua bảng trung gian book_author
    books = relationship("Book", secondary=book_author, back_populates="authors")

    def to_dict(self):
        return {
            "id": f"author_{self.id}",
            "name": self.name,
            "bio": self.bio,
        }


class Book(db.Model):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    price_vnd = Column(Integer, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)

    # Khóa ngoại và quan hệ N:1 với Category
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    category = relationship("Category", back_populates="books")

    # Quan hệ N:M với Author
    authors = relationship("Author", secondary=book_author, back_populates="books")

    # Quan hệ 1:N với Review
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category": self.category.to_dict() if self.category else None,
            "authors": [author.name for author in self.authors],
        }


class Review(db.Model):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rating = Column(Integer, nullable=False)

    # Quan hệ N:1 với Book
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    book = relationship("Book", back_populates="reviews")

    # Quan hệ N:1 với User
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="reviews")

    def to_dict(self):
        return {
            "id": f"review_{self.id}",
            "rating": self.rating,
            "book_id": f"book_{self.book_id}",
            "user_id": f"user_{self.user_id}",
        }