from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ThesisProject(models.Model):
    _name = "thesis.project"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Graduation Thesis Project"
    _order = "id desc"

    name = fields.Char(
        string="Project Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: "NEW",
    )
    title = fields.Char(string="Title", required=True)
    code = fields.Char(string="Project Code", readonly=True)
    batch_id = fields.Many2one(
        comodel_name="thesis.batch",
        string="Đợt đồ án",
        required=False,
        tracking=True,
        index=True,
        ondelete="restrict",
        domain=[("state", "not in", ["done", "cancelled"])],
        help="Đợt đồ án mà sinh viên tham gia.",
    )

    student_id = fields.Many2one(
        comodel_name="thesis.student",
        string="Sinh viên",
        required=True,
        tracking=True,
        ondelete="restrict",
        domain=[
            ("has_thesis_wish", "=", True),
            ("state", "in", ["eligible", "registered", "assigned"]),
        ],
        help=(
            "Chỉ hiển thị sinh viên đủ điều kiện, "
            "đã đăng ký nguyện vọng làm đồ án."
        ),
    )
    # Mã sinh viên dùng để hiển thị, tìm kiếm và đối chiếu import
    student_code = fields.Char(
        string="Mã sinh viên",
        related="student_id.student_code",
        store=True,
        readonly=True,
        index=True,
    )

    # Ngày sinh lấy từ hồ sơ sinh viên
    student_date_of_birth = fields.Date(
        string="Ngày sinh",
        related="student_id.date_of_birth",
        store=True,
        readonly=True,
    )

    # Lớp được lấy tự động từ sinh viên
    class_id = fields.Many2one(
        comodel_name="academic.class",
        string="Lớp",
        related="student_id.class_id",
        store=True,
        readonly=True,
        index=True,
    )
    student_phone = fields.Char(
        related = "student_id.phone",
        string = "Số điện thoại sinh viên",
        readonly = True,
    )
    student_email = fields.Char(
    related="student_id.email",
    string="Email sinh viên",
    readonly=True,
    )

    supervisor_id = fields.Many2one(
        comodel_name="thesis.lecturer",
        string="Giảng viên hướng dẫn",
        tracking=True,
        ondelete="restrict",
        domain="[('active', '=', True)]",
    )
    # Mã giảng viên dùng để hiển thị và đối chiếu import
    lecturer_code = fields.Char(
        string="Mã giảng viên",
        related="supervisor_id.lecturer_code",
        store=True,
        readonly=True,
        index=True,
    )
    status = fields.Selection(
    selection=[
        ("draft", "Khởi tạo hồ sơ"),
        ("registered", "Đã đăng ký đề tài"),
        ("assigned", "Đã giao đề tài và phân công GVHD"),
        ("accepted", "Sinh viên đã nhận đề tài"),
        ("in_progress", "Đang thực hiện đồ án"),
        ("submitted", "Đã nộp đồ án"),
        ("reviewing", "GVHD và phản biện đang đánh giá"),
        ("defense_approved", "Đủ điều kiện bảo vệ"),
        ("defended", "Đã bảo vệ"),
        ("graduation_review", "Đang xét tốt nghiệp"),
        ("completed", "Hoàn thành"),
        ("cancelled", "Đã hủy"),
    ],
    string="Trạng thái quy trình",
    default="draft",
    required=True,
    tracking=True,
)

    start_date = fields.Date(string="Start Date")
    due_date = fields.Date(string="Due Date")
    submission_date = fields.Date(string="Submission Date")
    defense_date = fields.Date(string="Defense Date")

    attachment = fields.Binary(string="Thesis File")
    attachment_name = fields.Char(string="Attachment Filename")

    grade = fields.Char(string="Grade")
    notes = fields.Text(string="Notes")

    assigned_by = fields.Many2one(
        "res.users",
        string="Assigned By",
        readonly=True,
        default=lambda self: self.env.user,
    )
    created_date = fields.Datetime(
        string="Created Date", readonly=True, default=fields.Datetime.now
    )
    @api.onchange("student_id")
    def _onchange_student_id(self):
        """Tự động lấy giảng viên đã phân công cho sinh viên."""
        if not self.student_id:
            self.supervisor_id = False
            return

        self.supervisor_id = self.student_id.supervisor_id
    @api.constrains("student_id", "status")
    def _check_active_project_per_student(self):
        """Mỗi sinh viên chỉ được có một đồ án đang hoạt động."""
        inactive_statuses = ["completed", "cancelled"]

        for project in self:
            if not project.student_id or project.status in inactive_statuses:
                continue

            duplicated_project = self.search(
                [
                    ("id", "!=", project.id),
                    ("student_id", "=", project.student_id.id),
                    ("status", "not in", inactive_statuses),
                ],
                limit=1,
            )

            if duplicated_project:
                raise ValidationError(
                    _(
                        "Sinh viên %(student)s đã có đồ án đang hoạt động: "
                        "%(project)s."
                    )
                    % {
                        "student": project.student_id.name,
                        "project": duplicated_project.name,
                    }
                )
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "NEW") == "NEW":
                seq = self.env["ir.sequence"].sudo().next_by_code("thesis.project")
                if seq:
                    vals["name"] = seq
                    vals["code"] = seq
                else:
                    vals["name"] = "TP/" + datetime.now().strftime("%Y%m%d%H%M%S")
                    vals["code"] = vals["name"]
        return super().create(vals_list)

    def action_register(self):
        """Bước 2: Xác nhận sinh viên đã đăng ký đề tài."""
        self.write({"status": "registered"})
        return True

    def action_assign(self):
        """Bước 3: Giao đề tài và phân công giảng viên hướng dẫn."""
        for project in self:
            if not project.student_id:
                raise ValidationError(
                    _("Vui lòng chọn sinh viên trước khi giao đề tài.")
                )

            if not project.supervisor_id:
                raise ValidationError(
                    _(
                        "Sinh viên %s chưa được phân công "
                        "giảng viên hướng dẫn."
                    )
                    % project.student_id.name
                )

            project.write(
                {
                    "status": "assigned",
                    "assigned_by": self.env.user.id,
                }
            )

        return True

    def action_accept(self):
        """Bước 4: Sinh viên xác nhận đã nhận đề tài."""
        self.write({"status": "accepted"})
        return True

    def action_start(self):
        """Bước 5: Bắt đầu thực hiện đồ án."""
        self.write(
            {
                "status": "in_progress",
                "start_date": fields.Date.context_today(self),
            }
        )
        return True

    def action_submit(self):
        """Bước 6: Sinh viên nộp đồ án."""
        self.write(
            {
                "status": "submitted",
                "submission_date": fields.Date.context_today(self),
            }
        )
        return True

    def action_start_review(self):
        """Bước 7: Chuyển hồ sơ sang giai đoạn đánh giá."""
        self.write({"status": "reviewing"})
        return True

    def action_approve_defense(self):
        """Bước 8: Xác nhận hồ sơ đủ điều kiện bảo vệ."""
        self.write({"status": "defense_approved"})
        return True

    def action_defend(self):
        """Bước 9: Xác nhận sinh viên đã bảo vệ đồ án."""
        self.write(
            {
                "status": "defended",
                "defense_date": fields.Date.context_today(self),
            }
        )
        return True

    def action_start_graduation_review(self):
        """Bước 10: Chuyển sang xét tốt nghiệp."""
        self.write({"status": "graduation_review"})
        return True

    def action_complete(self):
        """Bước 11: Hoàn thành toàn bộ quy trình."""
        self.write({"status": "completed"})
        return True

    def action_cancel(self):
        self.write({"status": "cancelled"})
        return True

    def action_set_grade(self, grade):
        for rec in self:
            rec.grade = grade
        return True
