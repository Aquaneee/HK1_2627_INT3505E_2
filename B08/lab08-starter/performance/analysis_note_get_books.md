# PHÂN TÍCH KẾT QUẢ KIỂM THỬ HIỆU NĂNG – API GET /books

**1. Kết quả kiểm thử**

Sử dụng Locust để kiểm thử hiệu năng endpoint `GET /books`, thu được các kết quả sau:

- Tổng số request: 272
- Số request thất bại: 0
- Thời gian phản hồi trung bình: 8,25 ms
- Thời gian phản hồi trung vị: 8 ms
- Thời gian phản hồi nhỏ nhất: 3 ms
- Thời gian phản hồi lớn nhất: 20 ms
- P95 (phân vị 95%): 13 ms
- P99 (phân vị 99%): 19 ms
- Thông lượng trung bình: 9,38 request/giây
- Kích thước nội dung phản hồi trung bình: 1.479 bytes

**2. Phân tích kết quả**

Endpoint `GET /books` hoạt động ổn định trong quá trình kiểm thử. Cả 272 request đều được xử lý thành công, không ghi nhận request thất bại, tương ứng với tỷ lệ lỗi 0%.

Thời gian phản hồi trung bình là 8,25 ms, cho thấy API có tốc độ phản hồi nhanh trong điều kiện kiểm thử hiện tại. Đặc biệt, 95% request có thời gian phản hồi không vượt quá 13 ms và 99% request không vượt quá 19 ms.

Thời gian phản hồi lớn nhất chỉ là 20 ms, cho thấy không xuất hiện tình trạng tăng độ trễ đáng kể trong lần kiểm thử này.

**3. Kết luận**

Endpoint `GET /books` đạt kết quả tốt trong kịch bản kiểm thử đã thực hiện. API có thời gian phản hồi thấp, thông lượng ổn định và không phát sinh request thất bại.

Tuy nhiên, kết quả này chỉ phản ánh hiệu năng trong phạm vi tải đã cấu hình trên Locust. Cần thực hiện thêm các bài kiểm thử với số lượng người dùng đồng thời cao hơn để đánh giá giới hạn chịu tải và khả năng mở rộng của API.