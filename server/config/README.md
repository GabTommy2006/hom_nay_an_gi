# Cấu hình server

`database.js` tạo pool mysql2 từ DB_HOST, DB_PORT, DB_NAME, DB_USER và DB_PASSWORD. Pool được tạo khi cần, giới hạn 5 kết nối; closeDatabase đóng kết nối khi shutdown hoặc kết thúc test.

`.env` nằm ở gốc, ngoài public và được gitignore. Không đặt mật khẩu trong code hoặc log. Khi triển khai remote, có thể cung cấp chứng chỉ PEM qua DB_SSL_CA để xác thực TLS.

Runtime đọc dữ liệu chỉ cần quyền SELECT. Tài khoản setup/import cần quyền tạo và sửa cấu trúc theo database/README.md. Không tự đổi hay tạo tài khoản khi khởi động website.
