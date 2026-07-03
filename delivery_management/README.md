# Delivery Management App

Ứng dụng quản lý giao nhận đồ án cho Odoo.

## Tính năng chính

1. **Quản lý giao hàng** - Tạo, theo dõi và quản lý các lần giao hàng
2. **Trạng thái giao hàng** - Draft, Confirmed, In Progress, Completed, Cancelled
3. **Liên kết đơn hàng** - Kết nối với Sale Orders
4. **Chi tiết sản phẩm** - Quản lý các sản phẩm trong từng lần giao hàng
5. **Thông tin lái xe** - Ghi chép tên lái xe và biển số xe
6. **Địa chỉ giao hàng** - Quản lý địa chỉ giao hàng chi tiết
7. **Người nhận** - Ghi chép thông tin người nhận
8. **Chữ ký** - Hỗ trợ chữ ký điện tử từ người nhận

## Cấu trúc thư mục

```
delivery_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── delivery_management.py
├── views/
│   └── delivery_management_view.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── delivery_data.xml
└── static/
    └── description/
        └── icon.png (tùy chọn)
```

## Cài đặt

1. Copy folder `delivery_management` vào Odoo addons folder hoặc để ở ngoài
2. Khởi động Odoo với flag `-d database_name` để tạo database
3. Vào Settings > Apps > Update Apps List
4. Tìm "Delivery Management" và click Install

## Sử dụng

- Vào menu **Delivery Management > Deliveries** để tạo lần giao hàng mới
- Nhập thông tin khách hàng, địa chỉ giao hàng, sản phẩm
- Confirm lần giao hàng
- Cập nhật trạng thái khi bắt đầu giao và khi hoàn thành

## Models

- **delivery.management** - Bản ghi giao hàng
- **delivery.line** - Chi tiết sản phẩm trong giao hàng
- **delivery.receiver** - Thông tin người nhận hàng
