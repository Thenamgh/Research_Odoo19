from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GraduationProject(models.Model):
    _name = "graduation.project"
    _description = "Graduation Project"
    # ==========================================
    # API 1 - @api.model
    # ==========================================
    @api.model
    def _default_state(self):
        """
        Trả về trạng thái mặc định khi tạo đồ án mới.
        """
        return "new"

    code = fields.Char(
        string="Mã đồ án",
        readonly=True,
        copy=False,
    )

    name = fields.Char(
        string="Tên đồ án",
        required=True
    )

    state = fields.Selection(
        [
            ("new", "Mới"),
            ("doing", "Đang thực hiện"),
            ("done", "Đã bảo vệ"),
        ],
        string="Trạng thái",
        default=_default_state,
    )
    score = fields.Float(
        string="Điểm"
    )

    result = fields.Char(
        string="Xếp loại",
        compute="_compute_result",
        store=True,
    )
    # ==========================================
    # API 2 - @api.onchange
    # ==========================================
    @api.onchange("name")
    def _onchange_name(self):
        """
        Kiểm tra tên đồ án khi người dùng đang nhập.
        Nếu tên quá ngắn thì cảnh báo.
        """

        if self.name and len(self.name) < 10:
            return {
                "warning": {
                    "title": "Cảnh báo",
                    "message": "Tên đồ án nên có ít nhất 10 ký tự."
                }
            }
    # ==========================================
    # API 3 - @api.constrains
    # ==========================================
    @api.constrains("name")
    def _check_name_length(self):

        for record in self:

            if record.name and len(record.name) < 10:
                raise ValidationError(
                "Tên đồ án phải có ít nhất 10 ký tự."
            )
            # ==========================================
    # API 4 - @api.depends
    # ==========================================
    @api.depends("score")
    def _compute_result(self):
        """
        Tự động tính xếp loại theo điểm.
        """

        for record in self:

            if record.score < 5:
                record.result = "Không đạt"

            elif record.score < 8:
                record.result = "Đạt"

            else:
                record.result = "Xuất sắc"
    # ==========================================
    # API 5 - @api.model_create_multi
    # ==========================================
    @api.model_create_multi
    def create(self, vals_list):
        """
        Tự động sinh mã đồ án khi tạo mới.
        """

        for vals in vals_list:

            if not vals.get("code"):

                vals["code"] = self.env["ir.sequence"].next_by_code(
                "graduation.project"
            )

        return super().create(vals_list)
    # ==========================================
    # API 6 - @api.returns
    # ==========================================
    # @api.model
    # @api.returns("self")
    # def get_project_by_code(self, code):
    #     """
    #     Tìm đồ án theo mã đồ án.
    #     Trả về một record của graduation.project.
    #     """

    #     return self.search(
    #         [("code", "=", code)],
    #         limit=1
    #     )

# # ==========================================
#     # API 1 - @api.onchange
#     # ==========================================

#     # @api.onchange("score")
#     # def _onchange_score(self):
#     #     """Tự điều chỉnh điểm trên giao diện"""

#     #     if self.score:

#     #         if self.score < 0:
#     #             self.score = 0

#     #         elif self.score > 10:
#     #             self.score = 10

#     # ==========================================
#     # API 2 - @api.constrains
#     # ==========================================

#     @api.constrains("score", "start_date", "end_date")
#     def _check_data(self):

#         for record in self:

#             if record.score < 0 or record.score > 10:
#                 raise ValidationError(
#                     "Điểm phải nằm trong khoảng từ 0 đến 10."
#                 )

#             if (
#                 record.start_date
#                 and record.end_date
#                 and record.end_date < record.start_date
#             ):
#                 raise ValidationError(
#                     "Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu."
#                 )

#     # ==========================================
#     # API 3 - @api.depends
#     # ==========================================

#     @api.depends("score")
#     def _compute_result(self):

#         for record in self:

#             if record.score >= 8:
#                 record.result = "Giỏi"

#             elif record.score >= 6.5:
#                 record.result = "Khá"

#             elif record.score >= 5:
#                 record.result = "Đạt"

#             else:
#                 record.result = "Không đạt"

#     # ==========================================
#     # API 4 + API 5
#     # @api.model_create_multi
#     # (Khuyến nghị cho Odoo mới)
#     # ==========================================

#     @api.model_create_multi
#     def create(self, vals_list):

#         for vals in vals_list:

#             if not vals.get("code"):

#                 count = self.search_count([]) + 1

#                 vals["code"] = "DA%04d" % count

#         return super().create(vals_list)

#     # ==========================================
#     # API 6 - @api.autovacuum
#     # ==========================================

#     @api.autovacuum
#     def _cleanup_old_projects(self):
#         """
#         Tự động xóa các đồ án ở trạng thái 'Mới'
#         đã tạo quá 365 ngày.
#         """

#         limit_date = fields.Date.today() - timedelta(days=365)

#         records = self.search([
#             ("state", "=", "new"),
#             ("create_date", "<", limit_date),
#         ])

#         if records:
#             records.unlink()
