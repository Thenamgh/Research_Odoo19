# -*- coding: utf-8 -*-

from odoo import fields, models


class AcademicCohort(models.Model):
    """
    Danh mục khóa học của sinh viên.

    Ví dụ:
    - Mã khóa: K15
    - Năm bắt đầu: 2024
    - Năm kết thúc dự kiến: 2028
    """

    _name = "academic.cohort"
    _description = "Khóa học"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_year desc, code"
    _rec_name = "name"

    # Mã khóa phục vụ tìm kiếm và import dữ liệu.
    code = fields.Char(
        string="Mã khóa",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Ví dụ: K15, K16, K17.",
    )

    # Tên đầy đủ của khóa học.
    name = fields.Char(
        string="Tên khóa",
        required=True,
        tracking=True,
        help="Ví dụ: Khóa 15.",
    )

    # Năm sinh viên bắt đầu nhập học.
    start_year = fields.Integer(
        string="Năm bắt đầu",
        required=True,
        tracking=True,
        help="Năm tuyển sinh hoặc năm nhập học.",
    )

    # Năm tốt nghiệp dự kiến.
    end_year = fields.Integer(
        string="Năm kết thúc dự kiến",
        required=True,
        tracking=True,
    )

    note = fields.Text(
        string="Ghi chú",
    )

    # Khóa đã kết thúc vẫn được lưu để tra cứu dữ liệu cũ.
    active = fields.Boolean(
        string="Đang hoạt động",
        default=True,
        tracking=True,
    )
