from odoo import models, fields

class GraduationProject(models.Model):
    _name = "graduation.project"
    _description = "Graduation Project"

    name = fields.Char(
        string="Tên đồ án",
        required=True
    )


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
