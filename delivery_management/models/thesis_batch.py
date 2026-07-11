from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class ThesisBatch(models.Model):
    _name = 'thesis.batch'
    _description = 'Đợt đăng ký đồ án tốt nghiệp'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'
    _rec_name = 'name'
    
    # Thông tin về đợt đăng ký đồ án
    name = fields.Char(
        string = 'Tên đợt đăng ký', 
        required = True, 
        tracking = True,
        help = 'Ví du: Đăng ký đồ án tốt nghiệp đợt 1 năm học 2025 - 2026',
        )
    academic_year = fields.Char(
        string = 'Năm học',
        required = True,
        tracking = True,
        help = 'Ví dụ: 2025 - 2026',
    )
    
    semeter = fields.Selection(
        selection = [
            ('1', 'Học kỳ 1'),
            ('2', 'Học kỳ 2'),
            ('3', 'Học kỳ hè'),
        ],
        string = 'Học kỳ',
        required = True,
        tracking = True,
    )