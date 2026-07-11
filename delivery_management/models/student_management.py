from odoo import models, fields, _
from odoo.exceptions import UserError


class ThesisStudent(models.Model):
    _name = "thesis.student"
    _description = "Sinh viên làm đồ án"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "student_code asc"
    _rec_name = "name"

    name = fields.Char(string="Họ và Tên", required=True, tracking=True)
    student_code = fields.Char(
        string="Mã Sinh Viên",
        required=True,
        copy=False,
    )
    class_name = fields.Char(string="Lớp")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Số điện thoại")

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

    def action_mark_eligible(self):
        """
        Xác nhận sinh viên đủ điều kiện làm đồ án/

        Khi xác nhận, hệ thống tự động:
        - Chuyển trạng thái sang 'Đủ điều kiện'
        - Lưu ngày xét điều kiện
        - Lưu người xét điều kiện của sinh viên"""

        for student in self:
            student.write(
                {
                    "state": "eligible",
                    "eligible_date": fields.Date.context_today(student),
                    "eligible_checked_by": self.env.user.id,
                }
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
