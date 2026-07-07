from odoo import models, fields

class ThesisLecturer(models.Model):
    name = 'thesis.lecturer'
    _description = 'Giang vien huong dan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'lecturer_code asc'
    
    name = fields.Char(
        string = 'Ho va ten',
        required = True,
    )
    lecturer_code = fields.Char(
        string = 'Ma Giang vien',
    )
    email = fields.Char(
        string = 'Email',
    )
    phone = fields.Char(
        string = 'So dien thoai',
    )
    department = fields.Char(
        string = 'Bo mon',
    )
    
    #Danh sacsh sinh vien dang huong dan
    student_ids = fields.One2many(
        comodel_name = 'thesis.student',
        inverse_name = 'supervisor_id',
        string = 'Danh sach sinh vien dang huong dan',
    )
    