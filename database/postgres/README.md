# Neon PostgreSQL

Website hỗ trợ `DB_PROVIDER=postgres` qua driver `pg`. Giao diện và các API giữ nguyên; Better Auth dùng trực tiếp PostgreSQL pool. Không bật Neon Auth vì website đang có hệ thống tài khoản riêng.

## Chạy với database đã chuyển

1. Cài Node.js 24 rồi chạy `npm ci`.
2. Tạo `.env` riêng trên máy, lấy thông tin qua kênh riêng của nhóm:

```dotenv
DB_PROVIDER=postgres
DATABASE_URL=postgresql://USER:PASSWORD@HOST-pooler.REGION.neon.tech/neondb?sslmode=require
BETTER_AUTH_URL=http://127.0.0.1:3000
BETTER_AUTH_SECRET=KHOA_BI_MAT_IT_NHAT_32_KY_TU
```

3. Chạy `npm start`. Không chạy `db:setup` hoặc nhập seed vào database chung đã có dữ liệu. Hai lệnh `db:setup`/`db:import` vẫn dành riêng cho MySQL và sẽ từ chối khi chọn PostgreSQL.

Trên Vercel, đặt `DB_PROVIDER=postgres`, `DATABASE_URL` bằng kết nối pooled, giữ nguyên `BETTER_AUTH_SECRET`, đặt `BETTER_AUTH_URL` bằng URL HTTPS chính thức. Không đưa mật khẩu hoặc URI vào Git, ảnh chụp hay README. Dùng database/branch Neon riêng nếu thử chức năng ghi; mọi thành viên dùng cùng database sẽ thấy dữ liệu sửa của nhau.

## Chuyển dữ liệu từ MySQL

`schema.sql` là cấu trúc PostgreSQL tương ứng, không chứa dữ liệu tài khoản. Script chuyển bảo toàn ID, JSON, thời gian UTC, liên kết, khóa ngoại, lịch sử chỉnh sửa, mật khẩu đã băm và phiên đăng nhập. Database đích phải trống.

```powershell
# .env lúc này vẫn là thông tin MySQL nguồn.
node --env-file=.env scripts/migrate-neon.mjs export .env.mysql-snapshot.json
# Lưu riêng URI Neon vào .env.neon-uri, không thêm dấu nháy.
node --env-file=.env scripts/migrate-neon.mjs apply .env.mysql-snapshot.json
```

Export dùng consistent snapshot chỉ đọc. Import chạy trong transaction, đối chiếu nội dung từng bảng rồi mới commit; lỗi sẽ rollback. Script từ chối đích đã có bảng, không xóa dữ liệu để chạy lại. Kết quả đối chiếu nằm trong `.env.neon-verification.json`. File snapshot chứa thông tin nhạy cảm, phải lưu riêng và không chia sẻ công khai.

Chốt thời điểm chuyển để tránh admin sửa MySQL sau snapshot. Giữ MySQL nguồn và cấu hình cũ để dự phòng. Nếu đã có ghi mới trên Neon, phải đối chiếu và chuyển các thay đổi đó trước khi quay lại MySQL; chỉ đổi URI sẽ làm mất khả năng nhìn thấy các thay đổi mới.

## Kiểm thử

```powershell
node --test tests/postgres.test.js
node --env-file=.env scripts/test-postgres.mjs .env.mysql-snapshot.json
```

Kiểm thử tích hợp cần URI trong `.env.neon-uri`, tự dùng host direct và tạo schema tên ngẫu nhiên. Nó sao chép snapshot vào schema riêng, kiểm tra API, đăng nhập/đăng xuất và quản trị, rồi xóa đúng schema kiểm thử trong `finally`; không sửa schema `public`. Tài khoản chạy kiểm thử cần quyền tạo schema. Nếu tiến trình bị dừng cưỡng bức, kiểm tra schema `hnag_test_*` trước khi dọn thủ công.

Các bài kiểm thử MySQL hiện có vẫn sử dụng MySQL riêng, không phải bằng chứng đã kiểm thử PostgreSQL.
