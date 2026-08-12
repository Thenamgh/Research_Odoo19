from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ThesisStudent(models.Model):
    _name = "thesis.student"
    _description = "Sinh viên làm đồ án"

    # Classical inheritance đối với hai mixin
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Delegation inheritance:
    # thesis.student ủy quyền các trường thông tin liên hệ
    # cho res.partner thông qua partner_id.
    _inherits = {
        "res.partner": "partner_id",
    }

    _order = "student_code asc"
    _rec_name = "name"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Thông tin liên hệ",
        required=True,
        ondelete="cascade",
        index=True,
        auto_join=True,
        delegate=True,
    )

    student_code = fields.Char(
        string="Mã Sinh Viên",
        required=True,
        copy=False,
    )
    # Thông tin cá nhân và đào tạo
    date_of_birth = fields.Date(
        string="Ngày sinh",
        tracking=True,
    )

    class_id = fields.Many2one(
        comodel_name="academic.class",
        string="Lớp hành chính",
        tracking=True,
        ondelete="restrict",
        help="Lớp hành chính hiện tại của sinh viên",
    )
    # Thông tin đào tạo tự động lấy từ lớp hành chính
    major_id = fields.Many2one(
        comodel_name="academic.major",
        string="Ngành đào tạo",
        related="class_id.major_id",
        store=True,
        readonly=True,
    )

    faculty_id = fields.Many2one(
        comodel_name="academic.faculty",
        string="Khoa",
        related="class_id.faculty_id",
        store=True,
        readonly=True,
    )

    cohort_id = fields.Many2one(
        comodel_name="academic.cohort",
        string="Khóa học",
        related="class_id.cohort_id",
        store=True,
        readonly=True,
    )
    # Trường cũ, tạm giữ để chuyển đổi dữ liệu
    class_name = fields.Char(
        string="Lớp (dữ liệu cũ)",
        help="Trường lớp dạng văn bản cũ, tạm giữ để chuyển đổi sang Lớp hành chính.",
    )
   
    # Bước 1: Thông tin xét điều kiện làm đồ án
    eligible_date = fields.Date(
        string="Ngày xét điều kiện",
        readonly=True,
        tracking=True,
    )
    eligible_checked_by = fields.Many2one(
        comodel_name="res.users",
        string="Người xét điều kiện",
        readonly=True,
        tracking=True,
    )
    eligible_note = fields.Text(
        string="Ghi chú xét điều kiện",
        help="Ghi rõ lý do sinh viên đủ hoặc không đủ điều kiện làm đồ án",
    )
    # Thông tin nguyện vọng làm đồ án
    has_thesis_wish = fields.Boolean(
        string="Có nguyện vọng làm đồ án",
        default=False,
        tracking=True,
        help="Đánh dấu nếu sinh viên có nguyện vọng làm đồ án tốt nghiệp",
    )
    wish_date = fields.Date(
        string="Ngày đăng ký nguyện vọng",
        readonly=True,
        tracking=True,
    )
    wish_note = fields.Text(
        string="Ghi chú nguyện vọng",
        help="Ghi chú bổ về nguyện vọng làm đồ án của sinh viên",
    )

    # Quan hệ với đề tài
    thesis_topic_id = fields.Many2one(
        comodel_name="thesis.topic",
        string="Đề tài đồ án",
        tracking=True,
    )
    supervisor_id = fields.Many2one(
        comodel_name="thesis.lecturer",
        string="Giảng Viên Hướng dẫn",
        tracking=True,
        domain=[("available_for_supervision", "=", True)],
        ondelete="set null",
    )

    state = fields.Selection(
        selection=[
            # 1: Lập danh sách và xét điều kiện
            ("new", "Chưa xét điều kiện"),
            ("eligible", "Đủ điều kiện"),
            # 2: Các bước tiếp theo
            ("registered", "Đã đăng ký đề tài"),
            ("assigned", "Đã phân công giảng viên"),
            ("submitted", "Đã nộp quyển"),
            ("defended", "Đã bảo vệ"),
            ("graduated", "Tốt nghiệp"),
        ],
        default="new",
        required=True,
        tracking=True,
        string="Trạng thái",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Khi tạo sinh viên, đồng bộ mã sinh viên sang trường ref
        của res.partner được tạo thông qua Delegation inheritance.
        """
        for vals in vals_list:
            if vals.get("student_code") and not vals.get("ref"):
                vals["ref"] = vals["student_code"]

        return super().create(vals_list)

    def write(self, vals):
        """
        Khi mã sinh viên thay đổi, đồng bộ lại res.partner.ref.
        """
        result = super().write(vals)

        if "student_code" in vals:
            for student in self:
                student.partner_id.ref = student.student_code

        return result

    @api.constrains("name")
    def _check_student_name(self):
        """
        res.partner.name không bắt buộc ở cấp database,
        nhưng hồ sơ sinh viên bắt buộc phải có họ tên.
        """
        for student in self:
            if not student.name:
                raise ValidationError(
                    _("Họ và tên sinh viên không được để trống.")
                )

    def action_register_wish(self):
        """
        Ghi nhận nguyện vọng làm đồ án của sinh viên
        Điều kiện:
        - Sinh viên phải được xác nhận đủ điều kiện
        - Sinh viên chưa đăng ký nguyện vọng trước đó"""
        for student in self:
            if student.state != "eligible":
                raise UserError(
                    _(
                        "Chỉ sinh viên đủ điều kiện mới được đăng ký nguyện vọng làm đồ án"
                    )
                )
            if student.has_thesis_wish:
                raise UserError(
                    _("Sinh viên đã đăng ký nguyện vọng làm đồ án trước đó")
                )
            student.write(
                {
                    "has_thesis_wish": True,
                    "wish_date": fields.Date.context_today(student),
                }
            )
        return True
