# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate   | RPS   |
| -------- | ----: | ---------: | -------: | -------: | -------------: | ----: |
| A        | 10    | 2          | 30s      | 23       | 0% (0 / 140)   | 4.76  |
| B        | 50    | 5          | 60s      | 44       | 0.07% (1/1373) | 23.12 |
| C        | 200   | 50         | 30s      | 120      | 0.11% (3/2851) | 97.10 |

1. Kịch bản có p95 cao nhất là gì? Dùng số liệu quan sát để giải thích.  
Kịch bản C có p95 cao nhất (120 ms ở mức tổng hợp; riêng POST /books đạt 150 ms và GET /books?year=[year] đạt 140 ms).  
Giải thích: Kịch bản C đẩy lượng người dùng đồng thời lên 200 users với tốc độ khởi tạo rất dồn dập (spawn rate = 50 users/s), tạo ra lưu lượng 97,10 RPS (gấp ~20 lần kịch bản A và ~4,2 lần kịch bản B). Dưới áp lực đồng thời cao trên kiến trúc Flask development server + SQLite (khóa ghi toàn cục ở mức tệp CSDL khi có đồng thời các lệnh POST /books và GET), các request phải xếp hàng chờ xử lý nên độ trễ đuôi p95 tăng vọt từ 23 ms -> 44 ms -> 120 ms.  

2. Endpoint nào tăng failure rate? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.  
Endpoint phát sinh lỗi: Chỉ có duy nhất GET /books?year=[year] ghi nhận lỗi ở kịch bản B (1/201 request ~ 0,50%) và kịch bản C (3/455 request ~0,66%), với thông báo CatchResponseError('Simulated 500 Internal Server Error').  
  
Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust:  
- Lỗi HTTP thực (Transport / HTTP Status Error): Là lỗi tự động bị Locust ghi nhận khi kết nối mạng thất bại (timeout, connection refused) hoặc server trả về mã trạng thái HTTP lỗi (4xx, 5xx) mà không có sự can thiệp chủ động từ kịch bản kiểm thử.  
- Lỗi đánh dấu trong Locust (CatchResponseError): Xảy ra khi script sử dụng khối with self.client.get(..., catch_response=True) as response: và chủ động gọi response.failure("...") (ở đây là lỗi 500 được mô phỏng/bắt có chủ đích trong logic kiểm thử để đánh dấu request đó là thất bại dù tầng giao vận vẫn nhận được phản hồi từ server).  

3. Với SLO giả định p95 < 300 ms, kịch bản nào đạt? Nêu giới hạn của phép đo.  
Kết quả: Cả 3 kịch bản A (23 ms), B (44 ms) và C (120 ms) đều đạt ngưỡng SLO p95 < 300 ms (ngay cả endpoint chậm nhất là POST /books ở kịch bản C cũng chỉ ở mức 150 ms).  
Giới hạn của phép đo: Không thể dùng kết quả này để khẳng định hiệu năng môi trường production vì phép đo chạy trên Flask development server kết hợp SQLite ngay trên máy cá nhân (độ trễ mạng loopback 127.0.0.1 gần bằng 0, dữ liệu nhỏ, thời gian chạy ngắn 30s–60s chưa phản ánh hiện tượng phình CSDL, tranh chấp lock dài hạn hay tải mạng thực tế).  

4. Nếu connection pool bị giới hạn ở 5, bạn sẽ kiểm chứng ảnh hưởng như thế nào?  
Cách kiểm chứng ảnh hưởng khi connection pool bị giới hạn ở 5:  
- Thiết lập cấu hình giới hạn kích thước pool tối đa bằng 5 (ví dụ pool_size=5, max_overflow=0 nếu dùng SQLAlchemy hoặc semaphore/pool giới hạn 5 kết nối đồng thời tới DB) và đặt pool_timeout rõ ràng.  
- Chạy lại kịch bản tải cao (như Kịch bản C với 200 users) rồi so sánh với kết quả gốc (p95 = 120 ms, 0,11% lỗi): quan sát sự gia tăng đột biến của độ trễ p95/p99 (do các request phải xếp hàng chờ mượn kết nối rảnh từ pool 5 kết nối), sụt giảm RPS, và sự xuất hiện của các lỗi timeout / HTTP 500 khi thời gian chờ vượt quá pool_timeout.

> Không điền số liệu giả định vào bảng. Không khẳng định hiệu năng production
> từ SQLite + Flask development server trên máy cá nhân.
