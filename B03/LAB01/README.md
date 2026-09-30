1. Xác định resources trong miền
   Dựa vào mô tả bài toán, các tài nguyên (resources) chính gồm có:
   Users / Profiles: Người dùng và hồ sơ cá nhân.
   Posts: Bài viết blog.
   Comments: Bình luận gắn với bài viết.
   Tags: Thẻ gắn kèm bài viết để phân loại.
   Follows / Followers: Mối quan hệ theo dõi giữa các người dùng.
2. Phân loại Collection, Item và Sub-resource
   - Collection Resource: Tập hợp nhiều thực thể (/posts, /users, /tags)
   - Item Resource: Một thực thể cụ thể xác định theo ID (/posts/{post_id}, /users/{user_id}, /tags/{tag_id})
   - Sub-resource: Tài nguyên nằm trong ngữ cảnh của tài nguyên cha (/posts/{post_id}/comments (bình luận của bài viết),
                                                                     /users/{user_id}/following (danh sách tác giả người đó theo dõi),
                                                                     /posts/{post_id}/tags (danh sách thẻ của bài viết))
3. Sơ đồ cây endpoint (API Versioning: /api/v1)
   /api/v1
  │
  ├── /users
  │   ├── POST          (Đăng ký/tạo user)
  │   ├── GET           (Lấy danh sách user)
  │   └── /{user_id}
  │       ├── GET       (Xem thông tin chi tiết / hồ sơ)
  │       ├── PUT/PATCH (Cập nhật hồ sơ)
  │       ├── /following
  │       │   ├── GET   (Danh sách tác giả đang theo dõi)
  │       │   └── POST  (Nhấn theo dõi tác giả khác)
  │       └── /followers
  │           └── GET   (Danh sách người theo dõi mình)
  │
  ├── /posts
  │   ├── GET           (Lấy danh sách bài viết - hỗ trợ filter ?tag=..., ?author=...)
  │   ├── POST          (Tạo bài viết mới)
  │   └── /{post_id}
  │       ├── GET       (Chi tiết bài viết)
  │       ├── PUT/PATCH (Chỉnh sửa bài viết)
  │       ├── DELETE    (Xóa bài viết)
  │       ├── /comments
  │       │   ├── GET   (Lấy danh sách bình luận của bài viết)
  │       │   └── POST  (Thêm bình luận mới vào bài viết)
  │       └── /tags
  │           └── POST  (Gắn thẻ cho bài viết)
  │
  ├── /comments
  │   └── /{comment_id}
  │       ├── PUT/PATCH (Chỉnh sửa bình luận)
  │       └── DELETE    (Xóa bình luận)
  │
  └── /tags
      ├── GET           (Danh sách tất cả các tag)
      └── POST          (Tạo mới tag)
