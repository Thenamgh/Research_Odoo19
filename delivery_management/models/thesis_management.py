from odoo import api, fields, models
from datetime import datetime


class ThesisProject(models.Model):
    _name = "thesis.project"
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

    student_id = fields.Many2one("res.partner", string="Student")
    student_phone = fields.Char(
        related="student_id.phone", string="Student Phone", readonly=True
    )
    student_email = fields.Char(
        related="student_id.email", string="Student Email", readonly=True
    )

    supervisor_id = fields.Many2one("res.users", string="Supervisor")

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "NEW") == "NEW":
                # Try to use sequence 'thesis.project' if defined, otherwise fallback to timestamp code
                seq = self.env["ir.sequence"].sudo().next_by_code("thesis.project")
                if seq:
                    vals["name"] = seq
                    vals["code"] = seq
                else:
                    vals["name"] = "TP/" + datetime.now().strftime("%Y%m%d%H%M%S")
                    vals["code"] = vals["name"]
        return super().create(vals_list)

    def action_assign(self):
        for rec in self:
            if rec.student_id:
                rec.status = "assigned"
                rec.assigned_by = self.env.user
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
