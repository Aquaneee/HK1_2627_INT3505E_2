# Báo Cáo Kiểm Toán Bảo Mật (Security Audit) - Social Network API

Tài liệu này liệt kê các điểm có nguy cơ rò rỉ thông tin nhạy cảm hoặc bị khai thác lỗ hổng bảo mật trên 3 endpoint: `POST /auth/login`, `POST /auth/refresh`, và `GET /posts/{id}`, cùng biện pháp khắc phục tương ứng.

---

### 1. Lộ danh sách người dùng qua thông báo lỗi (User Enumeration) tại `POST /auth/login`
* **Nguy cơ lộ:** Nếu API trả về thông báo lỗi quá chi tiết như `"Email không tồn tại trong hệ thống"` (status `404`) hoặc `"Mật khẩu không đúng"` (status `401`), hoặc thời gian phản hồi khi kiểm tra email tồn tại lâu hơn email không tồn tại (Timing Attack), kẻ tấn công có thể dò quét được danh sách email hợp lệ đang sử dụng mạng xã hội.
* **Cách khắc phục:** 
  * Luôn trả về cùng một mã trạng thái `401 Unauthorized` và một thông báo chung duy nhất: `"Email hoặc mật khẩu không chính xác"`.
  * Đảm bảo thời gian xử lý (constant-time comparison) đồng nhất dù email có tồn tại trong cơ sở dữ liệu hay không.

### 2. Lộ nội dung bài viết riêng tư qua phân biệt mã lỗi `403` và `404` (IDOR / Privacy Leak) tại `GET /posts/{id}`
* **Nguy cơ lộ:** Khi người dùng A truy cập bài viết ở chế độ `private` của người dùng B:
  * Nếu chưa kiểm tra quyền sở hữu/quan hệ bạn bè ở mức bản ghi (Broken Object Level Authorization - BOLA/IDOR), toàn bộ nội dung bài viết riêng tư sẽ bị lộ dù người gọi có scope `posts:read`.
  * Ngay cả khi chặn lại và trả về `403 Forbidden`, kẻ tấn công vẫn biết chắc chắn rằng UUID bài viết đó có tồn tại và đang ở chế độ riêng tư.
* **Cách khắc phục:**
  * Kiểm tra chặt chẽ quyền truy cập ở tầng dữ liệu: người gọi phải là tác giả, hoặc nằm trong danh sách bạn bè (nếu `visibility = friends`).
  * Cân nhắc trả về `404 Not Found` thay vì `403 Forbidden` đối với các bài viết `private` mà người gọi không được phép biết tới sự tồn tại của chúng.

### 3. Lộ và chiếm đoạt phiên đăng nhập do tái sử dụng Refresh Token (Token Replay / Theft) tại `POST /auth/refresh`
* **Nguy cơ lộ:** Nếu `refresh_token` không được thu hồi sau mỗi lần sử dụng hoặc được lưu trữ ở `localStorage` phía trình duyệt (dễ bị đọc trộm qua lỗi XSS), kẻ tấn công đánh cắp được `refresh_token` có thể âm thầm sinh ra vô số `access_token` mới để duy trì quyền truy cập trái phép lâu dài mà người dùng thật không hề hay biết.
* **Cách khắc phục:**
  * Áp dụng cơ chế **Refresh Token Rotation**: Mỗi lần gọi `POST /auth/refresh`, vô hiệu hóa ngay `refresh_token` cũ và cấp một `refresh_token` mới.
  * Áp dụng **Reuse Detection**: Nếu một `refresh_token` đã bị thu hồi lại được gửi lên một lần nữa, lập tức hủy toàn bộ chuỗi token (token family) của phiên đăng nhập đó và buộc người dùng đăng nhập lại.
  * Truyền `refresh_token` qua `HttpOnly, Secure, SameSite=Strict` cookie thay vì lưu trong `localStorage`.

### 4. Lộ dữ liệu nhạy cảm của tác giả do trả thừa trường (Excessive Data Exposure) tại `GET /posts/{id}`
* **Nguy cơ lộ:** Khi truy vấn bài viết và thực hiện `JOIN` hoặc eager-loading với bảng `Users` (tác giả bài viết), nếu lập trình viên trả thẳng đối tượng ORM ra JSON mà không lọc qua DTO/Schema, API rất dễ làm lộ các trường nhạy cảm của tác giả như `password_hash`, `email`, `phone_number`, hoặc `two_factor_secret`.
* **Cách khắc phục:**
  * Định nghĩa chặt chẽ Response Schema (DTO/Serializer) như `PostResponse` trong OpenAPI spec, chỉ trả về `author_id` hoặc thông tin công khai tối thiểu (`display_name`, `avatar_url`).
  * Cấu hình `additionalProperties: false` trong khâu kiểm thử hợp đồng API (Contract Testing).

### 5. Lộ thông tin mật khẩu và Token trên đường truyền hoặc Server Logs tại `/auth/*`
* **Nguy cơ lộ:** 
  * Nếu middleware ghi log của server tự động ghi lại toàn bộ `request.body` và `response.body`, mật khẩu dạng rõ (`plaintext password`) ở `/auth/login` cũng như `access_token`/`refresh_token` sẽ bị lưu trực tiếp vào file log hoặc hệ thống giám sát (ELK, Datadog).
  * Nếu truyền Token qua URL query parameter hoặc không bắt buộc dùng HTTPS, dữ liệu xác thực sẽ bị lộ qua lịch sử trình duyệt, proxy log và tấn công nghe lén (MITM).
* **Cách khắc phục:**
  * Cấu hình bộ lọc (Sanitizer/Redactor) ở tầng logging để che (`***REDACTED***`) các trường `password`, `access_token`, `refresh_token` và header `Authorization`.
  * Bắt buộc giao thức HTTPS (TLS 1.2+) và chỉ nhận thông tin nhạy cảm qua Request Body hoặc Header.

### 6. Lộ cấu trúc hệ thống nội bộ qua Stack Trace (Verbose Error Messages) ở các phản hồi lỗi `400` / `500`
* **Nguy cơ lộ:** Khi truyền tham số `id` sai định dạng vào `GET /posts/{id}` hoặc khi cơ sở dữ liệu gặp sự cố, nếu framework trả về nguyên văn lỗi mặc định (stack trace, câu lệnh SQL lỗi, tên bảng PostgreSQL/SQLite, đường dẫn file mã nguồn hoặc phiên bản thư viện), kẻ tấn công sẽ nắm được kiến trúc bên trong để chuẩn bị cho các cuộc tấn công sâu hơn (như SQL Injection).
* **Cách khắc phục:**
  * Tắt chế độ `DEBUG` trên môi trường Production.
  * Sử dụng Global Exception Handler để bắt mọi ngoại lệ chưa xác định, ghi log chi tiết ở phía server nhưng chỉ trả về cấu trúc `ErrorResponse` chuẩn hóa với thông báo chung cho phía client.
