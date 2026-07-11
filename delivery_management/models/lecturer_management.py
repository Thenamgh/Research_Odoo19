from odoo import api, fields, models


class ThesisLecturer(models.Model):
    _name = "thesis.lecturer"
    _description = "Giảng Viên Hướng Dẫn"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "lecturer_code asc"
    _rec_name = "name"

    # Thong tin Giang vien
    name = fields.Char(
        string="Họ và Tên",
        required=True,
        tracking=True,
    )
    lecturer_code = fields.Char(
        string="Mã Giảng Viên",
        required=True,
        copy=False,
        tracking=True,
    )
    email = fields.Char(
        string="Email",
    )
    phone = fields.Char(
        string="Số điện thoại",
    )
    department = fields.Char(
        string="Bộ môn",
    )
    date_of_birth = fields.Date(
        string="Ngày sinh",
        tracking=True,
    )
    gender = fields.Selection(
        selection=[
            ("male", "Nam"),
            ("female", "Nữ"),
            ("other", "Khác"),
        ],
        string="Giới tính",
        tracking=True,
    )

    # =========================================================
    # THÔNG TIN CHUYÊN MÔN
    # =========================================================

    academic_rank = fields.Selection(
        selection=[
            ("none", "Chưa có học hàm"),
            ("associate_professor", "Phó Giáo sư"),
            ("professor", "Giáo sư"),
        ],
        string="Học hàm",
        default="none",
        required=True,
        tracking=True,
        help="Học hàm của giảng viên: Phó Giáo sư hoặc Giáo sư.",
    )

    academic_degree = fields.Selection(
        selection=[
            ("bachelor", "Cử nhân/Kỹ sư"),
            ("master", "Thạc sĩ"),
            ("doctor", "Tiến sĩ"),
        ],
        string="Học vị",
        required=True,
        tracking=True,
        help=(
            "Học vị được sử dụng để xác định số sinh viên "
            "tối đa mà giảng viên được hướng dẫn."
        ),
    )

    specialization = fields.Char(
        string="Chuyên ngành",
        tracking=True,
        help="Chuyên ngành đào tạo hoặc nghiên cứu của giảng viên.",
    )

    # =========================================================
    # THÔNG TIN ĐƠN VỊ CÔNG TÁC
    # =========================================================

    faculty_id = fields.Many2one(
        comodel_name="academic.faculty",
        string="Khoa",
        required=True,
        tracking=True,
        ondelete="restrict",
        help="Khoa mà giảng viên đang công tác.",
    )

    department_id = fields.Many2one(
        comodel_name="academic.department",
        string="Bộ môn",
        required=True,
        tracking=True,
        ondelete="restrict",
        # Chỉ cho phép chọn Bộ môn thuộc Khoa đã chọn
        domain="[('faculty_id', '=', faculty_id)]",
        help="Bộ môn trực thuộc Khoa mà giảng viên đang công tác.",
    )

    employment_type = fields.Selection(
        selection=[
            ("full_time", "Đang công tác tại trường"),
            ("visiting", "Thỉnh giảng"),
        ],
        string="Trạng thái công tác",
        default="full_time",
        required=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Tài khoản hệ thống",
        tracking=True,
    )

    # Giới hạn hướng dẫn được tự động xác định theo học vị của Thầy/Cô
    max_students = fields.Integer(
        string="Số lượng sinh viên tối đa",
        compute="_compute_max_student",
        store=True,
        readonly=True,
        help=(
            "Hệ thống tự xác định theo học vị: "
            "Cử nhân/Kỹ sư: 0; Thạc sĩ: 10; Tiến sĩ: 15."
        ),
    )

    # Quan hệ với sinh viên (One2many)
    student_ids = fields.One2many(
        comodel_name="thesis.student",
        inverse_name="supervisor_id",
        string="Sinh viên đang hướng dẫn",
    )

    # Đếm số lượng sinh vên đang hướng dẫn
    student_count = fields.Integer(
        string="Số Sinh viên hiện tại",
        compute="_compute_student_count",
        store=False,
    )
    available_for_supervision = fields.Boolean(
        string="Có thể nhận hướng dẫn",
        compute="_compute_available_for_supervision",
        store=True,
        help=(
            "Được tự động đánh dấu khi giảng viên đang hoạt động"
            "và số sinh viên hiện tại chưa đạt giới hạn."
        ),
    )
    # Trạng thái giảng viên
    active = fields.Boolean(
        string="Đang hoạt động",
        default=True,
        tracking=True,
    )

    @api.depends("academic_degree")
    def _compute_max_students(self):
        """
        Tự động tính giới hạn hướng dẫn theo học vị

        @api.depends giúp Odoo tính lại max_students khi academic_degree thay đổi"""

        maximum_by_degree = {
            "bachelor": 0,
            "master": 10,
            "doctor": 15,
        }
        for lecturer in self:
            lecturer.max_students = maximum_by_degree.get(
                lecturer.academic_degree,
                0,
            )

    # Tính toán số lượng sinh viên đang hướng dẫn
    @api.depends("student_ids")
    def _compute_student_count(self):
        "Danh sách sinh viên đang hướng dẫn"
        for lecturer in self:
            lecturer.student_count = len(lecturer.student_ids)

    @api.depends("student_ids", "max_students", "active")
    def _compute_available_for_supervision(self):
        """
        Xác định giảng viên còn khả năng nhận sinh viên hay không

        @api.depends khai báo ba dữ liệu đầu vào
        Tự động tính lại khi các trường dữ liều đầu vào hay đổi
        1. student_ids: danh sách sinh viên đang hướng dẫn
        2. max_students: giới hạn được tính từ học vị
        3. active: trạng thái haojt động của giảng viên

        Odoo tự động tính lại khi một trong ba dữ liệu thay đổi"""
        for lecturer in self:
            lecturer.available_for_supervision = (
                lecturer.active
                and lecturer.max_students > 0
                and len(lecturer.student_ids) < lecturer.max_students
            )

    def is_available(self):
        """Kiểm tra giảng viên còn có thể nhân thêm sinh viên không?
        Method trả về Boolean đã được tính bỏi available_for_supervision"""
        self.ensure_one()
        return self.available_for_supervision
