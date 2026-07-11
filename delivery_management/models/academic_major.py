# -*- coding: utf-8 -*-

from odoo import fields, models


class AcademicMajor(models.Model):
    """
    Danh mục ngành đào tạo

    Ngành đào tạo được dùng để phân loại sinh viên và lớp học
    Mỗi ngành thuộc một khoa và có thể do một bộ môn phụ trách
    """

    _name = "academic.major"
    _description = "Ngành đào tạo"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "faculty_id, code"
    _rec_name = "name"

    # Mã ngành dùng để nhận diện và import dữ liệu
    code = fields.Char(
        string="Mã ngành",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Ví dụ: 7480201 hoặc CNTT",
    )

    # Tên đầy đủ của ngành đào tạo
    name = fields.Char(
        string="Tên ngành",
        required=True,
        tracking=True,
        help="Ví dụ: Công nghệ thông tin",
    )

    # Khoa quản lý ngành đào tạo
    faculty_id = fields.Many2one(
        comodel_name="academic.faculty",
        string="Khoa",
        required=True,
        tracking=True,
        ondelete="restrict",
    )

    # Bộ môn phụ trách chuyên môn của ngành
    department_id = fields.Many2one(
        comodel_name="academic.department",
        string="Bộ môn phụ trách",
        tracking=True,
        ondelete="restrict",
        domain="[('faculty_id', '=', faculty_id)]",
        help="Chỉ hiển thị các bộ môn thuộc khoa đã chọn",
    )

    # Trình độ đào tạo
    training_level = fields.Selection(
        selection=[
            ("bachelor", "Đại học"),
            ("master", "Thạc sĩ"),
            ("doctor", "Tiến sĩ"),
        ],
        string="Trình độ đào tạo",
        default="bachelor",
        required=True,
        tracking=True,
    )

    # Thời gian đào tạo tiêu chuẩn, tính theo năm
    duration_years = fields.Float(
        string="Thời gian đào tạo",
        default=4.0,
        help="Thời gian đào tạo tiêu chuẩn tính theo năm",
    )

    note = fields.Text(
        string="Ghi chú",
    )

    # Ngành ngừng tuyển sinh được lưu trữ thay vì xóa
    active = fields.Boolean(
        string="Đang hoạt động",
        default=True,
        tracking=True,
    )
