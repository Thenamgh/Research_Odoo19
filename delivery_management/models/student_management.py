from odoo import models, fields

class ThesisStudent(models.Model):
    _name = 'thesis.student'
    _description = 'Sinh vien lam do an'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'student_code asc'

    name = fields.Char(string='Ho va ten', required=True, tracking=True)
    student_code = fields.Char(string='Ma sinh vien', required=True, copy=False)
    class_name = fields.Char(string='Lop')
    email = fields.Char(string='Email')
    phone = fields.Char(string='So dien thoai')

    thesis_topic_id = fields.Many2one(
        comodel_name='thesis.topic',
        string='De tai do an',
        tracking=True,
    )
    supervisor_id = fields.Many2one(
        comodel_name='res.users',
        string='Giang vien huong dan',
        tracking=True,
    )

    state = fields.Selection(
        selection=[
            ('eligible',   'Du dieu kien'),
            ('registered', 'Da dang ky de tai'),
            ('assigned',   'Da phan cong GV'),
            ('submitted',  'Da nop quyen'),
            ('defended',   'Da bao ve'),
            ('graduated',  'Tot nghiep'),
        ],
        default='eligible',
        tracking=True,
        string='Trang thai',
    )
