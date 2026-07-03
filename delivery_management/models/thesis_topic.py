from odoo import api, fields, models


class ThesisTopic(models.Model):
    """Đề tài tốt nghiệp - Nhà trường giao cho sinh viên"""
    _name = 'thesis.topic'
    _description = 'Đề Tài Tốt Nghiệp'
    _order = 'create_date desc'

    name = fields.Char(string='Tên đề tài', required=True)
    code = fields.Char(string='Mã đề tài', copy=False, readonly=True)
    description = fields.Text(string='Mô tả')
    
    max_students = fields.Integer(
        string='Số sinh viên tối đa',
        default=2,
        help='Số sinh viên có thể nhận đề tài này'
    )
    assigned_count = fields.Integer(
        string='Số sinh viên đã nhận',
        compute='_compute_assigned_count',
        store=False
    )
    available_slots = fields.Integer(
        string='Vị trí còn trống',
        compute='_compute_available_slots',
        store=False
    )
    
    state = fields.Selection([
        ('available', 'Còn trống'),
        ('full', 'Đã đủ'),
        ('closed', 'Đóng'),
    ], string='Trạng thái', default='available', tracking=True)
    
    advisor_id = fields.Many2one(
        'res.users',
        string='Giáo viên hướng dẫn',
        required=True
    )
    
    created_date = fields.Datetime(
        string='Ngày tạo',
        readonly=True,
        default=fields.Datetime.now
    )
    
    assignment_ids = fields.One2many(
        'thesis.assignment',
        'topic_id',
        string='Danh sách sinh viên nhận'
    )
    
    def _compute_assigned_count(self):
        for topic in self:
            topic.assigned_count = len(topic.assignment_ids.filtered(lambda x: x.state == 'assigned'))
    
    def _compute_available_slots(self):
        for topic in self:
            topic.available_slots = max(0, topic.max_students - topic.assigned_count)
    
    def action_close_topic(self):
        """Đóng đề tài, không cho phép giao nữa"""
        self.write({'state': 'closed'})
    
    def action_reopen_topic(self):
        """Mở lại đề tài"""
        self.write({'state': 'available'})
    
    # ===== @api.model: Hàm không phụ thuộc record cụ thể =====
    @api.model
    def get_available_topics(self):
        """Lấy danh sách đề tài còn trống có thể giao"""
        return self.search([
            ('state', '=', 'available'),
            ('available_slots', '>', 0)
        ])
    
    @api.model
    def get_full_topics(self):
        """Lấy danh sách đề tài đã đủ sinh viên"""
        return self.search([('available_slots', '=', 0)])
    
    @api.model
    def can_student_receive_topic(self, student_id):
        """Kiểm tra sinh viên có thể nhận đề tài không (1 sinh viên chỉ nhận 1 đề tài)"""
        assignment = self.env['thesis.assignment'].search([
            ('student_id', '=', student_id),
            ('state', '=', 'assigned')
        ])
        return len(assignment) == 0
    
    @api.model
    def assign_topic_to_student(self, topic_id, student_id):
        """Giao đề tài cho sinh viên"""
        topic = self.browse(topic_id)
        
        # Kiểm tra đề tài có còn trống không
        if topic.available_slots <= 0:
            return {'status': 'error', 'message': 'Đề tài đã đủ sinh viên'}
        
        # Kiểm tra sinh viên chưa nhận đề tài khác
        if not self.can_student_receive_topic(student_id):
            return {'status': 'error', 'message': 'Sinh viên đã nhận đề tài khác'}
        
        # Tạo bản ghi giao nhận
        assignment = self.env['thesis.assignment'].create({
            'topic_id': topic_id,
            'student_id': student_id,
            'assigned_date': fields.Date.today(),
            'state': 'assigned'
        })
        
        # Cập nhật trạng thái đề tài nếu đã đủ
        if topic.available_slots - 1 == 0:
            topic.state = 'full'
        
        return {
            'status': 'success',
            'message': 'Giao đề tài thành công',
            'assignment_id': assignment.id
        }
    
    @api.model
    def get_topic_statistics(self):
        """Thống kê tổng quát về đề tài"""
        topics = self.search([])
        total = len(topics)
        available = len(self.get_available_topics())
        full = len(self.get_full_topics())
        
        return {
            'total_topics': total,
            'available_topics': available,
            'full_topics': full,
            'closed_topics': total - available - full
        }


class ThesisAssignment(models.Model):
    """Bản ghi giao/nhận đề tài giữa nhà trường và sinh viên"""
    _name = 'thesis.assignment'
    _description = 'Giao/Nhận Đề Tài'
    _order = 'assigned_date desc'

    topic_id = fields.Many2one(
        'thesis.topic',
        string='Đề tài',
        required=True,
        ondelete='cascade'
    )
    
    student_id = fields.Many2one(
        'res.partner',
        string='Sinh viên',
        required=True,
        domain=[('is_student', '=', True)]
    )
    
    student_code = fields.Char(
        string='Mã sinh viên',
        related='student_id.ref',
        readonly=True
    )
    
    assigned_date = fields.Date(
        string='Ngày giao',
        default=fields.Date.today,
        readonly=True
    )
    
    assigned_by = fields.Many2one(
        'res.users',
        string='Người giao',
        readonly=True,
        default=lambda self: self.env.user
    )
    
    state = fields.Selection([
        ('assigned', 'Đã giao'),
        ('accepted', 'Sinh viên đã nhận'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy'),
    ], string='Trạng thái', default='assigned', tracking=True)
    
    notes = fields.Text(string='Ghi chú')
    
    def action_accept(self):
        """Sinh viên xác nhận nhận đề tài"""
        self.write({'state': 'accepted'})
    
    def action_complete(self):
        """Đánh dấu đã hoàn thành"""
        self.write({'state': 'completed'})
    
    def action_cancel(self):
        """Hủy giao nhận - giải phóng vị trí"""
        self.write({'state': 'cancelled'})
        # Cập nhật trạng thái đề tài nếu từ đầy quay lại có trống
        if self.topic_id.available_slots > 0:
            self.topic_id.state = 'available'
