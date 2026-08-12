from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ThesisProjectExtension(models.Model):
    """
    Extension inheritance:
    - Không khai báo _name.
    - Mở rộng trực tiếp model thesis.project hiện có.
    - Các trường mới được bổ sung vào model/bảng thesis.project.
    """

    _inherit = "thesis.project"

    reviewer_id = fields.Many2one(
        comodel_name="thesis.lecturer",
        string="Giảng viên phản biện",
        tracking=True,
        ondelete="restrict",
        domain="[('active', '=', True), ('id', '!=', supervisor_id)]",
        help="Giảng viên phản biện phải khác giảng viên hướng dẫn.",
    )

    supervisor_approved = fields.Boolean(
        string="GVHD đồng ý cho bảo vệ",
        default=False,
        tracking=True,
    )

    reviewer_approved = fields.Boolean(
        string="Phản biện đồng ý cho bảo vệ",
        default=False,
        tracking=True,
    )

    ready_for_defense = fields.Boolean(
        string="Đủ điều kiện bảo vệ",
        compute="_compute_ready_for_defense",
        store=True,
        tracking=True,
    )

    @api.depends(
        "reviewer_id",
        "supervisor_approved",
        "reviewer_approved",
    )
    def _compute_ready_for_defense(self):
        """Chỉ đủ điều kiện khi đã có phản biện và cả hai bên đồng ý."""
        for project in self:
            project.ready_for_defense = bool(
                project.reviewer_id
                and project.supervisor_approved
                and project.reviewer_approved
            )

    @api.constrains("supervisor_id", "reviewer_id")
    def _check_reviewer_different_from_supervisor(self):
        """GVHD không được đồng thời là giảng viên phản biện."""
        for project in self:
            if (
                project.supervisor_id
                and project.reviewer_id
                and project.supervisor_id == project.reviewer_id
            ):
                raise ValidationError(
                    _("Giảng viên phản biện phải khác " "giảng viên hướng dẫn.")
                )

    def write(self, vals):
        """
        Nếu thay đổi giảng viên thì kết quả phê duyệt cũ
        không còn giá trị.
        """
        vals = dict(vals)

        if "supervisor_id" in vals:
            vals["supervisor_approved"] = False

        if "reviewer_id" in vals:
            vals["reviewer_approved"] = False

        return super().write(vals)

    def action_start_review(self):
        """
        Mở rộng phương thức gốc ở bước 7:
        phải phân công phản biện trước khi bắt đầu đánh giá.
        """
        for project in self:
            if not project.reviewer_id:
                raise ValidationError(
                    _(
                        "Vui lòng phân công giảng viên phản biện "
                        "trước khi chuyển hồ sơ sang giai đoạn đánh giá."
                    )
                )

        return super().action_start_review()

    def action_approve_defense(self):
        """
        Mở rộng phương thức gốc ở bước 8:
        chỉ chuyển sang defense_approved khi cả GVHD
        và phản biện đều đồng ý.
        """
        for project in self:
            if project.status != "reviewing":
                raise ValidationError(_("Hồ sơ phải đang ở giai đoạn đánh giá."))

            if not project.supervisor_approved:
                raise ValidationError(_("Giảng viên hướng dẫn chưa đồng ý cho bảo vệ."))

            if not project.reviewer_approved:
                raise ValidationError(_("Giảng viên phản biện chưa đồng ý cho bảo vệ."))

        # Gọi lại phương thức gốc trong thesis_management.py
        return super().action_approve_defense()
