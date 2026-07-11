# -*- coding: utf-8 -*-

from odoo import fields, models


class AcademicFaculty(models.Model):
    """
    Danh mục khoa trong trường đại học

    Model này được sử dụng chung cho:
    - Giảng viên
    - Sinh viên
    - Bộ môn
    - Ngành đào tạo
    """

    _name = "academic.faculty"
    _description = "Khoa"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code asc"
    _rec_name = "name"

    # Mã khoa dùng để phân biệt và phục vụ import dữ liệu
    code = fields.Char(
        string="Mã khoa",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Mã duy nhất của khoa, ví dụ: CNTT, QTKD",
    )

    # Tên đầy đủ của khoa
    name = fields.Char(
        string="Tên khoa",
        required=True,
        tracking=True,
        help="Ví dụ: Khoa Công Nghệ Thông Tin",
    )

    # Tên viết tắt dùng khi hiển thị trên danh sách hoặc báo cáo
    short_name = fields.Char(
        string="Tên viết tắt",
        tracking=True,
        help="Ví dụ: CNTT",
    )

    # Trưởng khoa/Phó khoa được liên kết với danh sách giảng viên
    # Trường này chưa bắt buộc vì khi mới tạo khoa có thể chưa nhập giảng viên
    dean_id = fields.Many2one(
        comodel_name="thesis.lecturer",
        string="Trưởng khoa",
        tracking=True,
        ondelete="set null",
    )

    email = fields.Char(
        string="Email",
    )

    phone = fields.Char(
        string="Số điện thoại",
    )

    address = fields.Text(
        string="Địa chỉ văn phòng",
    )

    note = fields.Text(
        string="Ghi chú",
    )

    # Dùng active để lưu trữ khoa ngừng hoạt động thay vì xóa dữ liệu
    active = fields.Boolean(
        string="Đang hoạt động",
        default=True,
        tracking=True,
    )
