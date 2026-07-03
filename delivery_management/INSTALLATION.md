# Installation Guide - Delivery Management App

## Yêu cầu hệ thống

- Odoo 14+ (hoạt động tốt trên Odoo 14, 15, 16, 17)
- Modules phụ thuộc:
  - base
  - stock
  - sale
  - mail (nếu muốn sử dụng thông báo email)

## Cách cài đặt

### Phương pháp 1: Cài đặt từ folder ngoài addons

1. **Copy folder `delivery_management` vào thư mục chứa Odoo**
   ```
   C:\Odoo_Research\Odoo_Platform\delivery_management
   ```

2. **Khởi động Odoo với parameter addons path**
   ```bash
   ./odoo-bin -d database_name -a delivery_management --addons-path=/path/to/odoo_platform
   ```

3. **Hoặc cấu hình trong odoo.conf**
   ```
   [options]
   addons_path = /path/to/odoo_platform,/path/to/addons
   ```

4. **Khởi động Odoo và vào Settings > Apps > Update Apps List**

5. **Tìm "Delivery Management" và click Install**

### Phương pháp 2: Cài đặt vào folder custom_addons

1. **Copy folder `delivery_management` vào `custom_addons`**
   ```
   C:\Odoo_Research\Odoo_Platform\custom_addons\delivery_management
   ```

2. **Khởi động Odoo bình thường**

3. **Settings > Apps > Update Apps List > Tìm và Install**

## Sử dụng

### 1. Tạo giao nhận mới

- Menu: **Delivery Management > Deliveries**
- Click "Create" button
- Nhập thông tin:
  - Khách hàng (bắt buộc)
  - Ngày giao hàng
  - Địa chỉ giao hàng
  - Sản phẩm

### 2. Quản lý trạng thái

- **Draft** - Soạn thảo, chưa xác nhận
- **Confirmed** - Đã xác nhận, chờ giao hàng
- **In Progress** - Đang giao hàng
- **Completed** - Giao hàng hoàn tất
- **Cancelled** - Hủy bỏ

### 3. Thêm sản phẩm

- Nhấn "Add a line" trong tab "Items"
- Chọn sản phẩm
- Nhập số lượng, giá đơn vị
- Hệ thống tự tính tổng cộng

### 4. Theo dõi thống kê

- Menu: **Delivery Management > Statistics**
- Xem số lượng giao hàng, tổng tiền, v.v.

## Các Model chính

### delivery.management
- Quản lý thông tin giao nhận
- Fields: tên, ngày giao, khách hàng, địa chỉ, trạng thái

### delivery.line
- Chi tiết sản phẩm trong giao nhận
- Fields: sản phẩm, số lượng, giá, tổng cộng

### delivery.receiver
- Thông tin người nhận hàng
- Fields: tên, điện thoại, email, chữ ký

### delivery.notification
- Thông báo giao hàng cho khách hàng
- Fields: loại thông báo, tin nhắn, thời gian gửi

### delivery.tracking
- Theo dõi vị trí giao hàng
- Fields: mã theo dõi, vị trí, trạng thái

## API Endpoints (Nếu cần tích hợp)

### Tạo giao nhận mới
```
POST /api/delivery.management/create
Content-Type: application/json

{
  "name": "DM/202601-001",
  "partner_id": 1,
  "delivery_date": "2026-07-01 10:00:00",
  "delivery_address": "123 Main St",
  "delivery_lines": [
    {"product_id": 1, "quantity": 2, "unit_price": 100}
  ]
}
```

### Lấy danh sách giao nhận
```
GET /api/delivery.management?state=confirmed
```

### Cập nhật trạng thái
```
PUT /api/delivery.management/1/update_state
Content-Type: application/json

{"state": "in_progress"}
```

## Troubleshooting

### Lỗi: Module not found
- **Giải pháp**: Kiểm tra addons_path trong odoo.conf
- Đảm bảo folder delivery_management nằm trong đường dẫn đó

### Lỗi: Cannot import name ...
- **Giải pháp**: Kiểm tra __init__.py files, đảm bảo syntax đúng

### Lỗi: Table does not exist
- **Giải pháp**: 
  1. Uninstall module
  2. Settings > Apps > Update Apps List
  3. Tìm Delivery Management và Install lại

### Lỗi: Permission denied
- **Giải pháp**: 
  - Kiểm tra file ir.model.access.csv
  - Gán quyền phù hợp cho user/group

## Support & Contribution

- Report bugs tại: [GitHub Issues]
- Contribute: [GitHub Pull Requests]

## License

MIT License - xem LICENSE file

---
**Created:** 2026-07-01
**Version:** 1.0
**Odoo Versions:** 14+
