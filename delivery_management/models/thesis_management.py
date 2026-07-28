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
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("submitted", "Submitted"),
            ("defended", "Defended"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
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

    def action_assign(self):
        """Xác nhận giao đồ án cho sinh viên"""
        for project in self:
            if not project.student_id:
                raise ValidationError(
                    _("Vui lòng chọn sinh viên trước khi giao đồ án")
                )
            if not project.supervisor_id:
                raise ValidationError(
                    _(
                        "Sinh viên %s chưa được phân công "
                        "giảng viên hướng dẫn"
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

    def action_start(self):
        self.write(
            {"status": "in_progress", "start_date": fields.Date.context_today(self)}
        )
        return True

    def action_submit(self):
        for rec in self:
            rec.status = "submitted"
            rec.submission_date = fields.Date.context_today(self)
        return True

    def action_defend(self):
        for rec in self:
            rec.status = "defended"
            rec.defense_date = fields.Date.context_today(self)
        return True

    def action_complete(self):
        self.write({"status": "completed"})
        return True

    def action_cancel(self):
        self.write({"status": "cancelled"})
        return True

    def action_set_grade(self, grade):
        for rec in self:
            rec.grade = grade
        return True
