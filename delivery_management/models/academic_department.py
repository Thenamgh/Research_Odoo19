# -*- coding: utf-8 -*-

from odoo import fields, models


class AcademicDepartment(models.Model):
    """
    Danh mục Bộ môn

    Mỗi bộ môn trực thuộc một khoa và được sử dụng để quản lý
    đơn vị chuyên môn của giảng viên
    """

    _name = "academic.department"
    _description = "Bộ môn"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "faculty_id, code"
    _rec_name = "name"

    # Mã bộ môn phục vụ tìm kiếm và import dữ liệu
    code = fields.Char(
        string="Mã bộ môn",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Ví dụ: CNPM, HTTT, KHDL, TTNT.",
    )

    # Tên đầy đủ của bộ môn
    name = fields.Char(
        string="Tên bộ môn",
        required=True,
        tracking=True,
        help="Ví dụ: Bộ môn Công nghệ Phần mềm",
    )

    # Khoa quản lý bộ môn
    faculty_id = fields.Many2one(
        comodel_name="academic.faculty",
        string="Khoa",
        required=True,
        tracking=True,
        ondelete="restrict",
        help="Khoa trực tiếp quản lý bộ môn",
    )

    # Trưởng bộ môn được chọn từ danh sách giảng viên
    # Chưa bắt buộc vì có thể tạo bộ môn trước khi nhập giảng viên
    head_id = fields.Many2one(
        comodel_name="thesis.lecturer",
        string="Trưởng bộ môn",
        tracking=True,
        ondelete="set null",
    )

    email = fields.Char(
        string="Email",
    )

    phone = fields.Char(
        string="Số điện thoại",
    )

    office = fields.Char(
        string="Văn phòng",
        help="Phòng hoặc địa điểm làm việc của bộ môn",
    )

    note = fields.Text(
        string="Ghi chú",
    )

    # Không xóa bộ môn đã ngừng hoạt động để bảo toàn dữ liệu cũ
    active = fields.Boolean(
        string="Đang hoạt động",
        default=True,
        tracking=True,
    )
