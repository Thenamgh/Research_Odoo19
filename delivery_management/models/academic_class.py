# -*- coding: utf-8 -*-

from odoo import fields, models


class AcademicClass(models.Model):
    """
    Danh mục lớp sinh viên.

    Lớp được sử dụng để phân loại sinh viên theo:
    - Ngành đào tạo
    - Khoa
    - Khóa học
    """

    _name = "academic.class"
    _description = "Lớp hành chính"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "cohort_id desc, code"
    _rec_name = "name"

    # Mã lớp phục vụ tìm kiếm và import sinh viên
    code = fields.Char(
        string="Mã lớp",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Ví dụ: DCCNTT11.10.2",
    )

    name = fields.Char(
        string="Tên lớp",
        required=True,
        tracking=True,
        help="Ví dụ: Công nghệ thông tin K11 - Lớp 2",
    )

    # Ngành đào tạo của lớp
    major_id = fields.Many2one(
        comodel_name="academic.major",
        string="Ngành đào tạo",
        required=True,
        tracking=True,
        ondelete="restrict",
    )

    # Khoa được tự động lấy từ ngành đào tạo
    # store=True để tìm kiếm, lọc và nhóm theo khoa
    faculty_id = fields.Many2one(
        comodel_name="academic.faculty",
        string="Khoa",
        related="major_id.faculty_id",
        store=True,
        readonly=True,
    )

    # Khóa tuyển sinh của lớp
    cohort_id = fields.Many2one(
        comodel_name="academic.cohort",
        string="Khóa học",
        required=True,
        tracking=True,
        ondelete="restrict",
    )

    # Cố vấn học tập được chọn từ danh sách giảng viên
    advisor_id = fields.Many2one(
        comodel_name="thesis.lecturer",
        string="Cố vấn học tập",
        tracking=True,
        ondelete="set null",
    )

    expected_student_count = fields.Integer(
        string="Sĩ số dự kiến",
        help="Số lượng sinh viên dự kiến của lớp.",
    )

    note = fields.Text(
        string="Ghi chú",
    )

    active = fields.Boolean(
        string="Đang hoạt động",
        default=True,
        tracking=True,
    )
