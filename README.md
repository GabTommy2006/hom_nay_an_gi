# Hôm nay ăn gì?

HTML/CSS/JavaScript + Node.js, không dùng EJS. Cần Node.js >=22.9.

## Chạy

`npm start` rồi mở http://127.0.0.1:3000.
`npm run dev` tự khởi động lại server khi sửa file. Không cần cài dependency cho bộ khung này.
Có thể chép `.env.example` thành `.env` để đổi HOST/PORT.

## Cấu trúc

- public/: tầng View, toàn bộ HTML/CSS/JS gửi xuống trình duyệt (không dùng EJS).
- server/app.js: HTTP server và phục vụ file tĩnh.
- server/routes/dish.routes.js: ánh xạ URL và HTTP method sang controller.
- server/controllers/dish.controller.js: nhận yêu cầu và trả JSON cho frontend.
- server/models/: tầng Model đọc/lọc dữ liệu, thay bằng truy vấn database sau.
- server/config/, middleware/, services/, validators/, utils/: khung chuẩn bị cho backend; mỗi thư mục có hướng dẫn trách nhiệm.
- server/views/: dành sẵn cho template nếu sau này cần; View hiện tại vẫn là public/, không dùng EJS.
- database/migrations/, database/seeds/: dành cho cấu trúc và dữ liệu khởi tạo database sau này.
- scripts/, tests/: dành cho công cụ bảo trì và kiểm thử khi triển khai backend.
- data/food.json: 105 món/bánh/đồ uống, 7 nhóm ẩm thực và các bữa ăn; 78 món có quán liên kết trực tiếp.
- docs/DEVELOPMENT.md: hướng dẫn triển khai tiếp.

## API hiện có

- `restaurants.html`: danh sách thử 105 địa điểm Đà Nẵng từ Excel, có tìm kiếm/lọc/phân trang và chi tiết.
- `GET /api/restaurants`: danh sách quán (q, category, meal, priceTier, page, pageSize).
- `GET /api/restaurants/dn-013`: chi tiết một địa điểm.
- Dữ liệu và nguồn ảnh: `docs/RESTAURANT-DATA.md`; kiểm tra bằng `node --test tests/restaurants.test.js`.

- GET /api/dishes
- GET /api/dishes?cuisine=viet&meal=sang
- GET /api/dishes/pho-bo

Khi chạy Node.js, /js/data.js được tạo từ data/food.json để giao diện và API dùng chung dữ liệu. Sửa dữ liệu mẫu tại data/food.json. public/js/data.js là bản dự phòng cũ cho chế độ xem tĩnh, không tự đồng bộ; nên dùng npm start.

Đã có hai công thức frontend và danh bạ địa điểm đọc từ JSON qua backend MVC. Chưa có database SQL, đăng nhập/admin hoặc tích hợp đơn hàng.
