# Tasks API Specification & Implementation

Bài tập về nhà Buổi 4: Viết đặc tả API bằng OpenAPI 3.x và tích hợp Swagger UI vào ứng dụng Flask.

## Cấu trúc Repository
- `openapi.yaml`: File đặc tả API chuẩn OpenAPI 3.0.3 cho 5 endpoints.
- `app.py`: Ứng dụng Flask phục vụ tài nguyên API, đường dẫn `/openapi.json` và giao diện `/docs`.

## Hướng dẫn chạy ứng dụng
1. Cài đặt môi trường:
   pip install flask pyyaml
2. Chạy server:
   python app.py
3. Truy cập Swagger UI tại: http://localhost:5000/docs

2 Quyết định thiết kế khó nhất (Design Decisions)
  - Sử dụng phương thức PATCH thay vì PUT cho cập nhật công việc (/tasks/{taskId}):
    Lý do: Thay vì bắt buộc người dùng truyền toàn bộ đối tượng Task (PUT), sử dụng PATCH kết hợp với schema UpdateTaskInput chứa các thuộc tính optional cho phép client
    chỉ cập nhật riêng lẻ từng thuộc tính mong muốn (như thay đổi status từ open sang done) mà không làm thay đổi hay mất dữ liệu của các thuộc tính khác.
  
  - Quản lý linh hoạt Authorization ở cấp độ Global và Endpoint-level:
    Lý do: Toàn bộ API được thiết lập bảo mật chuẩn Bearer JWT ở mức global (security: [{bearerAuth: []}]). Việc tái sử dụng $ref cho các mẫu Response lỗi chuẩn
    (Unauthorized, NotFound, ValidationError) trong khối components giúp giữ cho file đặc tả ngắn gọn, nhất quán và dễ mở rộng khi bổ sung thêm tính năng trong tương lai.
