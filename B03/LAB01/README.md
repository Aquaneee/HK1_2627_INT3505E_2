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
      ```text
   /api/v1
   ├── /users
   │   ├── POST          # Tạo tài khoản / Đăng ký
   │   ├── GET           # Danh sách người dùng
   │   └── /{user_id}
   │       ├── GET       # Lấy thông tin hồ sơ (profile)
   │       ├── PUT/PATCH # Cập nhật hồ sơ
   │       ├── /following
   │       │   ├── GET   # Danh sách tác giả đang theo dõi
   │       │   └── POST  # Nhấn theo dõi một tác giả
   │       └── /followers
   │           └── GET   # Danh sách người theo dõi mình
   │
   ├── /posts
   │   ├── GET           # Lấy danh sách bài viết (?tag=..., ?author=...)
   │   ├── POST          # Tạo bài viết mới
   │   └── /{post_id}
   │       ├── GET       # Lấy chi tiết bài viết
   │       ├── PUT/PATCH # Sửa nội dung bài viết
   │       ├── DELETE    # Xóa bài viết
   │       ├── /comments
   │       │   ├── GET   # Lấy tất cả bình luận của bài viết
   │       │   └── POST  # Viết bình luận vào bài viết
   │       └── /tags
   │           └── POST  # Gắn thẻ (tag) vào bài viết
   │
   ├── /comments
   │   └── /{comment_id}
   │       ├── PUT/PATCH # Sửa bình luận
   │       └── DELETE    # Xóa bình luận
   │
   └── /tags
       ├── GET           # Lấy danh sách tất cả các tag
       └── POST          # Tạo tag mới
   ```
