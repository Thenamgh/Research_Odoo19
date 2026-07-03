"""
Ví dụ sử dụng @api.model trong hệ thống giao nhận đề tài
"""

# ============================================================================
# EXAMPLE 1: Lấy danh sách đề tài còn trống
# ============================================================================
def example_1():
    """Lấy tất cả đề tài còn trống để hiển thị cho sinh viên"""
    topic_model = env['thesis.topic']
    
    # Gọi hàm @api.model
    available_topics = topic_model.get_available_topics()
    
    print(f"Số đề tài còn trống: {len(available_topics)}")
    for topic in available_topics:
        print(f"  - {topic.name} (còn {topic.available_slots} vị trí)")


# ============================================================================
# EXAMPLE 2: Kiểm tra sinh viên có thể nhận đề tài không
# ============================================================================
def example_2():
    """Kiểm tra trước khi giao đề tài"""
    topic_model = env['thesis.topic']
    
    student_id = 1  # Mã sinh viên
    
    # Gọi hàm @api.model để kiểm tra
    can_receive = topic_model.can_student_receive_topic(student_id)
    
    if can_receive:
        print("Sinh viên có thể nhận đề tài mới")
    else:
        print("Sinh viên đã có đề tài, không thể nhận thêm")


# ============================================================================
# EXAMPLE 3: Giao đề tài cho sinh viên
# ============================================================================
def example_3():
    """Giao đề tài cho sinh viên"""
    topic_model = env['thesis.topic']
    
    topic_id = 5
    student_id = 10
    
    # Gọi hàm @api.model để giao
    result = topic_model.assign_topic_to_student(topic_id, student_id)
    
    if result['status'] == 'success':
        print(f"✓ {result['message']}")
        print(f"  Assignment ID: {result['assignment_id']}")
    else:
        print(f"✗ {result['message']}")


# ============================================================================
# EXAMPLE 4: Thống kê tổng quát
# ============================================================================
def example_4():
    """Xem thống kê về đề tài"""
    topic_model = env['thesis.topic']
    
    # Gọi hàm @api.model thống kê
    stats = topic_model.get_topic_statistics()
    
    print("=== THỐNG KÊ ĐỀ TÀI ===")
    print(f"Tổng số đề tài: {stats['total_topics']}")
    print(f"Đề tài còn trống: {stats['available_topics']}")
    print(f"Đề tài đã đủ: {stats['full_topics']}")
    print(f"Đề tài đã đóng: {stats['closed_topics']}")


# ============================================================================
# EXAMPLE 5: Lấy danh sách đề tài đã đủ
# ============================================================================
def example_5():
    """Xem đề tài nào đã đủ sinh viên"""
    topic_model = env['thesis.topic']
    
    # Gọi hàm @api.model
    full_topics = topic_model.get_full_topics()
    
    print(f"Số đề tài đã đủ sinh viên: {len(full_topics)}")
    for topic in full_topics:
        print(f"  - {topic.name}")


# ============================================================================
# EXAMPLE 6: Sử dụng trong wizard để giao hàng loạt
# ============================================================================
class ThesisTopicBulkAssign(models.TransientModel):
    """Wizard giao đề tài hàng loạt"""
    _name = 'thesis.topic.bulk.assign'
    _description = 'Giao Đề Tài Hàng Loạt'
    
    topic_ids = fields.Many2many('thesis.topic', string='Các đề tài')
    student_ids = fields.Many2many('res.partner', string='Các sinh viên')
    
    def action_assign_bulk(self):
        """Giao đề tài cho tất cả sinh viên"""
        topic_model = self.env['thesis.topic']
        
        # Lấy danh sách đề tài còn trống từ @api.model
        available = topic_model.get_available_topics()
        
        # Lọc chỉ lấy đề tài được chọn
        selected = self.topic_ids.filtered(lambda t: t in available)
        
        results = {'success': 0, 'failed': 0}
        
        for student in self.student_ids:
            for topic in selected:
                if topic.available_slots > 0:
                    # Sử dụng @api.model assign_topic_to_student
                    result = topic_model.assign_topic_to_student(topic.id, student.id)
                    
                    if result['status'] == 'success':
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                    
                    break  # Mỗi sinh viên chỉ nhận 1 đề tài
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Giao Đề Tài',
                'message': f"Thành công: {results['success']}, Thất bại: {results['failed']}",
                'type': 'success' if results['failed'] == 0 else 'warning',
            }
        }
