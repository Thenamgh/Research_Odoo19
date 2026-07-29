# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ThesisBatch(models.Model):
    """Quản lý một đợt thực hiện đồ án tốt nghiệp."""

    _name = "thesis.batch"
    _description = "Đợt đồ án tốt nghiệp"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "academic_year desc, date_start desc, id desc"
    _rec_name = "name"

    name = fields.Char(
        string="Tên đợt đồ án",
        required=True,
        tracking=True,
        help="Ví dụ: Đợt 1 đồ án tốt nghiệp năm học 2026 - 2027",
    )

    code = fields.Char(
        string="Mã đợt",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Ví dụ: DATN-2026-01",
    )

    academic_year = fields.Char(
        string="Năm học",
        required=True,
        tracking=True,
        help="Ví dụ: 2026 - 2027",
    )

    semester = fields.Selection(
        selection=[
            ("1", "Học kỳ 1"),
            ("2", "Học kỳ 2"),
            ("summer", "Học kỳ hè"),
        ],
        string="Học kỳ",
        required=True,
        tracking=True,
    )

    # Mốc thời gian tổng thể
    registration_start_date = fields.Date(
        string="Bắt đầu đăng ký",
        tracking=True,
    )

    registration_end_date = fields.Date(
        string="Kết thúc đăng ký",
        tracking=True,
    )

    date_start = fields.Date(
        string="Bắt đầu thực hiện",
        required=True,
        tracking=True,
    )

    submission_deadline = fields.Date(
        string="Hạn nộp đồ án",
        required=True,
        tracking=True,
    )

    defense_date = fields.Date(
        string="Ngày bảo vệ dự kiến",
        tracking=True,
    )

    date_end = fields.Date(
        string="Kết thúc đợt",
        required=True,
        tracking=True,
    )

    state = fields.Selection(
        selection=[
            ("draft", "Dự thảo"),
            ("registration", "Đang đăng ký"),
            ("in_progress", "Đang thực hiện"),
            ("defense", "Đang bảo vệ"),
            ("done", "Đã kết thúc"),
            ("cancelled", "Đã hủy"),
        ],
        string="Trạng thái",
        default="draft",
        required=True,
        tracking=True,
    )

    note = fields.Text(
        string="Ghi chú",
    )

    active = fields.Boolean(
        string="Đang hoạt động",
        default=True,
        tracking=True,
    )

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "Mã đợt đồ án đã tồn tại.",
    )

    @api.constrains(
        "registration_start_date",
        "registration_end_date",
        "date_start",
        "submission_deadline",
        "defense_date",
        "date_end",
    )
    def _check_date_sequence(self):
        """Kiểm tra thứ tự các mốc thời gian chính của đợt đồ án."""
        for batch in self:
            if (
                batch.registration_start_date
                and batch.registration_end_date
                and batch.registration_start_date > batch.registration_end_date
            ):
                raise ValidationError(
                    _("Ngày bắt đầu đăng ký phải trước ngày kết thúc đăng ký.")
                )

            if batch.date_start > batch.submission_deadline:
                raise ValidationError(
                    _("Ngày bắt đầu thực hiện phải trước hạn nộp đồ án.")
                )

            if batch.submission_deadline > batch.date_end:
                raise ValidationError(_("Hạn nộp đồ án phải trước ngày kết thúc đợt."))

            if batch.defense_date and batch.defense_date > batch.date_end:
                raise ValidationError(
                    _("Ngày bảo vệ dự kiến không được sau ngày kết thúc đợt.")
                )

    def action_open_registration(self):
        self.write({"state": "registration"})
        return True

    def action_start_batch(self):
        self.write({"state": "in_progress"})
        return True

    def action_start_defense(self):
        self.write({"state": "defense"})
        return True

    def action_done(self):
        self.write({"state": "done"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True

    def action_reset_to_draft(self):
        self.write({"state": "draft"})
        return True
