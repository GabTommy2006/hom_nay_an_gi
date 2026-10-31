# Hôm nay ăn gì?

HTML/CSS/JavaScript + Node.js, không dùng EJS. Cần Node.js >=22.9.

## Chạy

`npm start` rồi mở http://127.0.0.1:3000.
`npm run dev` tự khởi động lại server khi sửa file. Không cần cài dependency cho bộ khung này.
Có thể chép `.env.example` thành `.env` để đổi HOST/PORT.

## Cấu trúc

- public/: toàn bộ HTML/CSS/JS gửi xuống trình duyệt.
- server/app.js: HTTP server và phục vụ file tĩnh.
- server/routes/dishes.js: API danh sách, lọc và chi tiết món.
- server/repositories/: tầng đọc dữ liệu, thay bằng truy vấn database sau.
- data/food.json: dữ liệu mẫu 30 món, ẩm thực và bữa ăn.
- docs/DEVELOPMENT.md: hướng dẫn triển khai tiếp.

## API hiện có

- GET /api/dishes
- GET /api/dishes?cuisine=viet&meal=sang
- GET /api/dishes/pho-bo

Khi chạy Node.js, /js/data.js được tạo từ data/food.json để giao diện và API dùng chung dữ liệu. Sửa dữ liệu mẫu tại data/food.json. public/js/data.js là bản dự phòng cũ cho chế độ xem tĩnh, không tự đồng bộ; nên dùng npm start.

Chưa có database thật, công thức, đăng nhập/admin hoặc tích hợp đơn hàng.
