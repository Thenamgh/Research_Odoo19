# EIT Odoo Platform 2026 — Research_Odoo19

Dự án tùy biến trên nền tảng **Odoo 19 Community**, phục vụ quản lý quy trình giao nhận đồ án tốt nghiệp cho sinh viên ngành Công nghệ Thông tin.

Repo này chứa **Odoo 19 core đầy đủ** + module custom `delivery_management` do nhóm phát triển.

---

## 1. Giới thiệu

| | |
|---|---|
| **Nền tảng** | Odoo 19.0 Community |
| **Module custom** | `delivery_management` |
| **Chức năng chính** | Quản lý đề tài đồ án (`thesis.topic`), phân công hướng dẫn (`thesis.assignment`), theo dõi tiến độ giao nhận (`delivery.tracking`), thống kê & báo cáo (`delivery.report`, `delivery.statistics`) |
| **Ngôn ngữ** | Python 3.11+, XML (views), PostgreSQL |

---

## 2. Cấu trúc thư mục

```
Research_Odoo19/
├── odoo/                    # Odoo 19 core
├── addons/                  # Addons chuẩn đi kèm Odoo
├── delivery_management/     # Module custom của nhóm (quản lý đồ án tốt nghiệp)
│   ├── models/
│   ├── views/
│   ├── security/
│   ├── data/
│   └── __manifest__.py
├── debian/
├── doc/
├── setup/
└── odoo.conf                # File cấu hình chạy local (KHÔNG commit thông tin nhạy cảm)
```

---

## 3. Yêu cầu môi trường

- Python 3.11+
- PostgreSQL 14+ (đang dùng cổng `5433` trong cấu hình mẫu)
- pip, virtualenv (khuyến khích dùng venv riêng, không commit vào repo)

---

## 4. Cài đặt lần đầu

### 4.1. Clone repo

```bash
git clone https://github.com/Thenamgh/Research_Odoo19.git
cd Research_Odoo19
```

### 4.2. Cài dependencies Python

```bash
pip install -r odoo/requirements.txt
```

### 4.3. Tạo file cấu hình `odoo.conf`

Tạo file `odoo.conf` ở thư mục gốc (file này **không** được commit lên Git vì chứa thông tin nhạy cảm — xem mục 6). Nội dung mẫu:

```ini
[options]
admin_passwd = <mật khẩu admin đã mã hóa hoặc để plain khi test local>
db_host = localhost
db_port = 5433
db_user = odoo
db_password = odoo
db_name = graduation_project_db
dbfilter = ^graduation_project_db$
addons_path = <đường-dẫn-tuyệt-đối-tới-project>/odoo/addons,<đường-dẫn-tuyệt-đối-tới-project>/addons,<đường-dẫn-tuyệt-đối-tới-project>
http_interface = 127.0.0.1
```

**Quan trọng:** `addons_path` phải trỏ đến **thư mục cha chứa module** (thư mục gốc project), **không trỏ thẳng vào** `delivery_management` — Odoo sẽ tự quét các thư mục con để tìm `__manifest__.py`.

### 4.4. Khởi tạo database và cài module

```bash
python odoo-bin -c odoo.conf -i delivery_management -d graduation_project_db
```

---

## 5. Quy trình chạy hằng ngày

**Chạy server bình thường:**

```bash
python odoo-bin -c odoo.conf -d graduation_project_db
```

**Sau khi pull code mới có thay đổi model/view/security:**

```bash
python odoo-bin -c odoo.conf -u delivery_management -d graduation_project_db --stop-after-init
python odoo-bin -c odoo.conf -d graduation_project_db
```

**Sau khi pull code chỉ thay đổi logic Python thuần** (không đổi model/view): chỉ cần restart server, không bắt buộc `-u`.

Xem chi tiết quy trình Git hằng ngày (branch, commit, PR) tại tài liệu workflow riêng của nhóm.

---

## 6. Lưu ý bảo mật — KHÔNG commit các thông tin sau

- File `odoo.conf` thật (chứa mật khẩu DB, admin_passwd) — chỉ commit file `odoo.conf.example` nếu cần chia sẻ mẫu
- Thư mục `filestore/`, `sessions/` (dữ liệu người dùng thật)
- File `.venv/`, `venv/`, `__pycache__/`
- Dữ liệu sinh viên thật dùng để test (nên dùng dữ liệu giả lập)

Các mục này đã được khai báo trong `.gitignore`.

---

## 7. Sự cố thường gặp

| Vấn đề | Nguyên nhân | Cách xử lý |
|---|---|---|
| `KeyError: 'thesis.project'` / `404 Not Found` khi gọi model | `addons_path` sai, hoặc module chưa cài trên DB đang dùng | Kiểm tra `addons_path` trỏ đúng thư mục gốc chứa `delivery_management`; chạy lại `-u delivery_management` |
| `module delivery_management: not installable, skipped` | `addons_path` trỏ thẳng vào thư mục module thay vì thư mục cha | Sửa `addons_path` bỏ phần `/delivery_management` ở cuối |
| Module bị kẹt ở trạng thái "Upgrading" | Update bị ngắt giữa chừng (đóng terminal khi đang chạy `-u`) | Chạy lại `-u delivery_management --stop-after-init`, đợi chạy xong hẳn mới đóng terminal |
| Field mới không hiện trên UI | Chưa update module sau khi đổi model | Chạy `-u delivery_management` |
| Push code lên GitHub bị nặng/ngắt kết nối | Lịch sử Git quá lớn hoặc mạng không ổn định | Dọn lịch sử Git (xóa `.git` cũ, tạo lại commit sạch), tăng `http.postBuffer` trước khi push |

---

## 8. Team

Dự án được phát triển bởi nhóm **EIT Odoo Platform 2026**, Khoa Công nghệ Thông tin.

- Repo: [`Research_Odoo19`](https://github.com/Thenamgh/Research_Odoo19)
- Quy trình làm việc chi tiết: xem file hướng dẫn workflow riêng của nhóm.