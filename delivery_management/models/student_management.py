from odoo import models, fields

class ThesisStudent(models.Model):
    _name = 'thesis.student'
    _description = 'Sinh viên làm đồ án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'student_code asc'

    name = fields.Char(string='Họ và Tên', required=True, tracking=True)
    student_code = fields.Char(string='Mã Sinh Viên', required=True, copy=False)
    class_name = fields.Char(string='Lớp')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Số điện thoại')

    thesis_topic_id = fields.Many2one(
        comodel_name='thesis.topic',
        string='Đề tài đồ án',
        tracking=True,
    )
    supervisor_id = fields.Many2one(
        comodel_name='thesis.lecturer',
        string='Giảng Viên Hướng dẫn',
        tracking=True,
    )

    state = fields.Selection(
        selection=[
            ('eligible',   'Đủ điều kiện'),
            ('registered', 'Đã đăng ký đề tài'),
            ('assigned',   'Đã phân công giảng viên'),
            ('submitted',  'Đã nộp quyển'),
            ('defended',   'Đã bảo vệ'),
            ('graduated',  'Tốt nghiệp'),
        ],
        default='eligible',
        tracking=True,
        string='Trạng thái',
    )
