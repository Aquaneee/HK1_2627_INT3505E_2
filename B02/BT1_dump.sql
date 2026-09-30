BEGIN TRANSACTION;
CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                price REAL
            );
INSERT INTO "books" VALUES(1,'Clean Code','Robert C. Martin','978-0132350884',30.0);
CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT NOT NULL,
                total REAL NOT NULL
            );
INSERT INTO "orders" VALUES(1,'pending',60.0);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('books',1);
INSERT INTO "sqlite_sequence" VALUES('orders',1);
COMMIT;
