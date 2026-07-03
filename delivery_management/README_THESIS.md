# Hệ Thống Giao Nhận Đề Tài - Sử dụng @api.model

## Tổng Quan

Module này quản lý quá trình nhà trường giao đề tài tốt nghiệp cho sinh viên.

## Các Model Chính

### 1. **thesis.topic** - Đề Tài Tốt Nghiệp
Quản lý các đề tài mà nhà trường cung cấp.

**Trường dữ liệu:**
- `name`: Tên đề tài
- `code`: Mã đề tài (tự động)
- `description`: Mô tả chi tiết
- `max_students`: Số sinh viên tối đa có thể nhận (mặc định 2)
- `assigned_count`: Số sinh viên đã nhận (tính toán)
- `available_slots`: Vị trí còn trống (tính toán)
- `state`: Trạng thái (available/full/closed)
- `advisor_id`: Giáo viên hướng dẫn
- `assignment_ids`: Danh sách giao nhận

### 2. **thesis.assignment** - Bản Ghi Giao Nhận
Ghi nhận việc giao đề tài từ nhà trường đến sinh viên.

**Trường dữ liệu:**
- `topic_id`: Đề tài được giao
- `student_id`: Sinh viên nhận
- `assigned_date`: Ngày giao (mặc định hôm nay)
- `assigned_by`: Người giao (mặc định người dùng hiện tại)
- `state`: Trạng thái (assigned/accepted/completed/cancelled)
- `notes`: Ghi chú thêm

---

## Các Hàm @api.model (Không phụ thuộc record cụ thể)

### 1. **get_available_topics()**
Lấy danh sách đề tài còn trống có thể giao.

```python
topic_model = env['thesis.topic']
available = topic_model.get_available_topics()

# Kết quả: danh sách thesis.topic có state='available' và available_slots > 0
for topic in available:
    print(f"{topic.name} - Còn {topic.available_slots} vị trí")
```

### 2. **get_full_topics()**
Lấy danh sách đề tài đã đủ sinh viên.

```python
topic_model = env['thesis.topic']
full = topic_model.get_full_topics()

# Kết quả: danh sách thesis.topic có available_slots = 0
for topic in full:
    print(f"{topic.name} - Đã đủ {topic.assigned_count} sinh viên")
```

### 3. **can_student_receive_topic(student_id)**
Kiểm tra sinh viên có thể nhận đề tài không (mỗi sinh viên chỉ nhận 1 đề tài).

```python
topic_model = env['thesis.topic']
student_id = 10

can_receive = topic_model.can_student_receive_topic(student_id)

if can_receive:
    print("Sinh viên có thể nhận đề tài mới")
else:
    print("Sinh viên đã có đề tài khác")
```

### 4. **assign_topic_to_student(topic_id, student_id)**
Giao đề tài cho sinh viên (kiểm tra điều kiện tự động).

```python
topic_model = env['thesis.topic']
result = topic_model.assign_topic_to_student(topic_id=5, student_id=10)

if result['status'] == 'success':
    print(f"✓ {result['message']}")
    print(f"Assignment ID: {result['assignment_id']}")
else:
    print(f"✗ {result['message']}")
```

**Kết quả trả về:**
```python
{
    'status': 'success' or 'error',
    'message': 'Mô tả chi tiết',
    'assignment_id': <id> (nếu thành công)
}
```

### 5. **get_topic_statistics()**
Thống kê tổng quát về đề tài.

```python
topic_model = env['thesis.topic']
stats = topic_model.get_topic_statistics()

print(f"Tổng đề tài: {stats['total_topics']}")
print(f"Còn trống: {stats['available_topics']}")
print(f"Đã đủ: {stats['full_topics']}")
print(f"Đã đóng: {stats['closed_topics']}")
```

**Kết quả trả về:**
```python
{
    'total_topics': <int>,
    'available_topics': <int>,
    'full_topics': <int>,
    'closed_topics': <int>
}
```

---

## Ví Dụ Sử Dụng Thực Tế

### Ví dụ 1: Giao đề tài cho sinh viên

```python
# Lấy sinh viên và đề tài
student = env['res.partner'].search([('is_student', '=', True)], limit=1)
topic = env['thesis.topic'].get_available_topics()[0]

# Giao đề tài
result = env['thesis.topic'].assign_topic_to_student(topic.id, student.id)

# Kết quả
if result['status'] == 'success':
    # Tạo project/thesis cho sinh viên
    thesis_project = env['thesis.project'].create({
        'title': topic.name,
        'student_id': student.id,
        'supervisor_id': topic.advisor_id.user_id.id,
        'status': 'assigned'
    })
```

### Ví dụ 2: Dashboard thống kê

```python
# Lấy thống kê
stats = env['thesis.topic'].get_topic_statistics()

# Hiển thị
{
    'total': stats['total_topics'],
    'empty': stats['available_topics'],
    'full': stats['full_topics'],
    'closed': stats['closed_topics'],
    'percentage_filled': (stats['full_topics'] / stats['total_topics'] * 100) if stats['total_topics'] > 0 else 0
}
```

### Ví dụ 3: Giao hàng loạt

```python
# Danh sách sinh viên
students = env['res.partner'].search([('is_student', '=', True)])

# Danh sách đề tài còn trống
available_topics = env['thesis.topic'].get_available_topics()

# Giao từng sinh viên
for i, student in enumerate(students):
    if i < len(available_topics):
        topic = available_topics[i]
        result = env['thesis.topic'].assign_topic_to_student(topic.id, student.id)
        print(f"Giao {topic.name} cho {student.name}: {result['status']}")
```

---

## Trạng Thái Luồng

### Đề Tài (thesis.topic):
```
available → full
   ↓
 closed → available (mở lại)
```

### Giao Nhận (thesis.assignment):
```
assigned → accepted → completed
   ↓
cancelled → (giải phóng vị trí)
```

---

## SQL Queries (Nếu cần truy vấn trực tiếp)

```sql
-- Lấy đề tài còn trống
SELECT * FROM thesis_topic 
WHERE state = 'available' AND max_students - assigned_count > 0;

-- Thống kê theo giáo viên
SELECT advisor_id, COUNT(*) as total, 
       SUM(CASE WHEN available_slots > 0 THEN 1 ELSE 0 END) as available
FROM thesis_topic
GROUP BY advisor_id;

-- Sinh viên chưa có đề tài
SELECT s.* FROM res_partner s
WHERE s.is_student = TRUE
AND s.id NOT IN (
    SELECT DISTINCT student_id FROM thesis_assignment WHERE state = 'assigned'
);
```

---

## Files Được Tạo

```
delivery_management/
├── models/
│   ├── thesis_topic.py                 (Model thesis.topic & thesis.assignment với @api.model)
│   ├── thesis_topic_examples.py        (Ví dụ sử dụng)
│   └── __init__.py                     (Import models)
├── views/
│   └── thesis_topic_view.xml           (UI views cho model)
└── README_THESIS.md                    (File này)
```

---

## Lưu Ý

1. **@api.model không cần record**: Các hàm `@api.model` được gọi trên model class, không cần instance cụ thể
2. **Kiểm tra tự động**: Hàm `assign_topic_to_student` tự động kiểm tra điều kiện trước khi giao
3. **Tính toán động**: `assigned_count` và `available_slots` tính toán từ `assignment_ids`
4. **Giải phóng vị trí**: Khi hủy giao nhận, vị trí sẽ được giải phóng

---

## Next Steps

1. Thêm security rules trong `ir.model.access.csv`
2. Tạo reports để xuất danh sách giao nhận
3. Tích hợp workflow approval
4. Thêm notifications khi sinh viên nhận đề tài
