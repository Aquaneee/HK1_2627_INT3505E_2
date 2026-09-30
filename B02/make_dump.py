import sqlite3

# Kết nối tới file database của bạn
conn = sqlite3.connect("app.db")

# Xuất toàn bộ schema và dữ liệu ra file dump.sql
with open("dump.sql", "w", encoding="utf-8") as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")

conn.close()
print("Đã tạo file dump.sql thành công!")