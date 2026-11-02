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

Đã có 14 công thức frontend và danh bạ địa điểm đọc từ JSON qua backend MVC. Chưa có database SQL, đăng nhập/admin hoặc tích hợp đơn hàng.


### Yêu thích và công thức (frontend)

Trang `favorites.html` lưu ID món/quán trong localStorage (`hnag:favorites:v1`) của trình duyệt hiện tại, không có tài khoản hay đồng bộ giữa thiết bị. Nút trái tim ở danh mục, kết quả, công thức và chi tiết quán; đồng bộ trạng thái giữa các tab cùng origin. Khi trình duyệt chặn ghi, giao diện báo lỗi và không hiện thành công giả. Quán tải qua API đọc hiện có; lỗi tải không xóa ID đã lưu.

8 công thức: xôi xoài, bruschetta, phở bò phiên bản nhanh, Pad Thai tôm, pizza Margherita, onigiri cá ngừ, canh kim chi, risotto nấm. Sáu công thức bổ sung được biên soạn tiếng Việt với định lượng điều chỉnh, dẫn nguồn ở từng trang (Canada’s Food Guide, Good Food, Just One Cookbook, Maangchi, Diabetes UK). Không phải công thức xác nhận của quán; không tự lan truyền nhãn dinh dưỡng/chay. Tất cả dùng chung bộ chọn 1–12 người và đánh dấu bước nấu.


Bổ sung đợt 03/11/2026: bún chả bản áp chảo, bánh xèo tôm thịt, bibimbap bản rau phổ biến, kimbap nhân xúc xích, mapo tofu giảm dầu/cay và Tom Yum tôm nước trong. Tổng 14 công thức. Nguồn và các điều chỉnh ghi ở từng trang; không đổi nhãn dinh dưỡng hoặc ăn chay.


### Giao diện admin — chỉ frontend

Mở `/admin-login.html` để vào bản xem thử, hoặc `/admin.html` để xem trực tiếp. Email/mật khẩu readonly là dữ liệu mẫu, không được gửi đi hoặc lưu lại. Chưa có xác thực hay phân quyền và không có API ghi.

7 mục: tổng quan, quán, món, món tại quán, công thức, duyệt thông tin và tài khoản. Quán đọc bằng các endpoint GET hiện có; món và công thức đọc dữ liệu frontend. Tài khoản để trạng thái chưa kết nối, không tạo người dùng/thống kê giả. Form thêm/sửa lưu bản nháp riêng vào localStorage (`hnag:admin-drafts:v1`), khôi phục khi tải lại trên cùng trình duyệt. Có xóa bản nháp với bước xác nhận và đồng bộ giữa các tab. Nếu đọc/ghi bị lỗi, giao diện báo rõ và không báo lưu thành công giả. Không thay đổi file JSON, công thức công khai, trạng thái nhãn chay/dinh dưỡng hoặc liên kết đặt hàng thật. Bảng có tìm kiếm không dấu, lọc bản nháp, phân trang; dialog có kiểm tra trường, chống liên kết trùng, nguồn https, bàn phím và giao diện mobile/sáng/tối. Đường dẫn admin không được bảo vệ cho tới khi có backend.
