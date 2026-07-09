from odoo import api, models, fields

class ThesisLecturer(models.Model):
    _name = 'thesis.lecturer'
    _description = 'Giảng Viên Hướng Dẫn'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'lecturer_code asc'
    _rec_name = 'name'
    
    # Thong tin Giang vien
    name = fields.Char(
        string = 'Họ và Tên',
        required = True,
        tracking = True,
    )
    lecturer_code = fields.Char(
        string = 'Mã Giảng Viên',
        required = True,
        copy = False,
        tracking = True,
    )
    email = fields.Char(
        string = 'Email',
    )
    phone = fields.Char(
        string = 'Số điện thoại',
    )
    department = fields.Char(
        string = 'Bộ môn',
    )
    user_id = fields.Many2one(
        comodel_name = 'res.users',
        string = 'Tài khoản hệ thống',
        tracking = True,
    )
    
    # Giới hạn số lượng sinh viên được hướng dẫn
    max_students = fields.Integer(
        string = 'Số lượng sinh viên tối đa',
        default = 5,
        help = 'Số lượng sinh viên tối đa mà giảng viên có thể hướng dẫn'
    )
    
    # Quan hệ với sinh viên (One2many)
    student_ids = fields.One2many(
        comodel_name = 'thesis.student',
        inverse_name = 'supervisor_id',
        string = 'Sinh viên đang hướng dẫn',
    )
    
    # Đếm số lượng sinh vên đang hướng dẫn
    student_count = fields.Integer(
        string = 'Số Sinh viên hiện tại',
        compute = '_compute_student_count',
        store = False,
    )
    
    # Trạng thái giảng viên
    active = fields.Boolean(
        string = 'Đang hoạt động',
        default = True,
    )
    
    # Tính toán số lượng sinh viên đang hướng dẫn
    @api.depends('student_ids')
    def _compute_student_count(self):
        "Danh sách sinh viên đang hướng dẫn"
        for rec in self:
            rec.student_count = len(rec.student_ids)
    
    def is_available(self):
        """Kiểm tra xem giảng viên còn có thể nhân thêm sinh viên không?"""
        self.ensure_one()
        return self.student_count < self.max_students
            
    