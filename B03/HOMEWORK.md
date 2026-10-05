Phân tích các vấn đề trong API cũ
Thiết kế URI và HTTP Methods:
- Lạm dụng động từ trong URL (/addItemToCart, /removeItemFromCart, /checkOut, /makeOrder) thay vì định danh bằng danh từ (resource-based)
- Xóa sản phẩm dùng POST thay vì DELETE
- Đặt đuôi mở rộng file (.php, .json) trực tiếp trên URL làm lộ công nghệ triển khai và vi phạm tính trừu tượng của REST

Xác thực & Truyền dữ liệu nhạy cảm:
- Truyền userId qua query param: dễ bị tấn công IDOR (Insecure Direct Object References). Danh tính người dùng cần được trích xuất từ Authentication Token (JWT, Bearer token, Cookie/Session)
- API /login truyền username và password trực tiếp qua Query String: thông tin đăng nhập sẽ bị ghi log trên trình duyệt, proxy và server, gây nguy cơ bảo mật nghiêm trọng
- Các tham số tạo mới/sửa đổi (productId, qty) nên đặt trong Request Body (JSON) thay vì Query String

HTTP Status Code & Response Lỗi:
- Trả về HTTP Code 200 OK nhưng body lại chứa lỗi FAIL. Cần dùng đúng HTTP Status Code (ví dụ: 400 Bad Request, 422 Unprocessable Entity, hoặc 409 Conflict)
- Chuẩn hóa cấu trúc response lỗi theo chuẩn (RFC 7807 hoặc cấu trúc đồng nhất)

Thiếu API Versioning:
- Không có tiền tố phiên bản (/api/v1/), gây khó khăn khi cần nâng cấp và duy trì khả năng tương thích ngược (backward compatibility)

THIẾT KẾ LẠI CÁC ENDPOINT

Đăng ký tài khoản:
API Cũ: POST /signup
API Mới: POST /api/v1/auth/register
Ghi chú: Dữ liệu gửi qua Request Body dạng JSON: {"email": "...", "password": "..."}

Đăng nhập:
API Cũ: POST /login?username=u&password=p
API Mới: POST /api/v1/auth/login
Ghi chú: Đưa username và password vào Request Body để bảo mật, không để trên Query String. Trả về access token/JWT

Xem thông tin giỏ hàng:
API Cũ: GET /getCartItems
API Mới: GET /api/v1/cart
Ghi chú: Tự động nhận diện người dùng qua Authorization Header (Token), không cần truyền userId trên URL

Thêm sản phẩm vào giỏ hàng:
API Cũ: POST /addItemToCart?userId=42&productId=99&qty=2
API Mới: POST /api/v1/cart/items
Ghi chú: Truyền dữ liệu vào Request Body: {"productId": 99, "quantity": 2}

Xóa sản phẩm khỏi giỏ hàng:
API Cũ: POST /removeItemFromCart
API Mới: DELETE /api/v1/cart/items/{itemId}
Ghi chú: Sử dụng phương thức chuẩn DELETE và đưa itemId vào path parameter

Khởi tạo tiến trình thanh toán (Checkout):
API Cũ: GET /checkOut?userId=42
API Mới: POST /api/v1/checkouts
Ghi chú: Sử dụng POST vì hành động khởi tạo phiên checkout làm thay đổi trạng thái giao dịch

Tạo đơn hàng (Đặt hàng):
API Cũ: POST /makeOrder?userId=42
API Mới: POST /api/v1/orders
Ghi chú: Dữ liệu đơn hàng (địa chỉ, hình thức thanh toán) đặt trong Request Body

Xem chi tiết đơn hàng:
API Cũ: GET /getOrder?orderId=1001
API Mới: GET /api/v1/orders/1001
Ghi chú: Đặt mã đơn hàng trực tiếp trong đường dẫn tài nguyên

Xem danh sách đơn hàng của người dùng:
API Cũ: GET /listUserOrders?userId=42
API Mới: GET /api/v1/orders
Ghi chú: Tự động lọc theo user đăng nhập, hỗ trợ phân trang qua query param

Lấy danh sách sản phẩm:
API Cũ: GET /productsList.json?cat=phones
API Mới: GET /api/v1/products?category=phones
Ghi chú: Loại bỏ đuôi mở rộng file (.json), sử dụng header Accept: application/json

CHUẨN HÓA RESPONSE VÀ MÃ LỖI HTTP
Thay vì trả về HTTP Status Code 200 kèm body "status": "FAIL", cần sử dụng đúng mã trạng thái HTTP để phản ánh chính xác lỗi
HTTP Status Code đề xuất khi xảy ra lỗi nghiệp vụ (ví dụ hết hàng): 422 Unprocessable Entity (hoặc 400 Bad Request / 409 Conflict)
Header: Content-Type: application/json
Cấu trúc Response lỗi:
{
  "success": false,
  "error": {
    "code": "OUT_OF_STOCK",
    "message": "Sản phẩm yêu cầu hiện đã hết hàng hoặc không đủ số lượng tồn kho.",
    "details": [
      {
        "field": "quantity",
        "productId": 99,
        "availableQuantity": 0
      }
    ]
  },
  "timestamp": "2026-10-05T18:00:00Z"
}
