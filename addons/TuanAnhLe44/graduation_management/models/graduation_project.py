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
    # ==================================================
    # Demo Environment
    # ==================================================
    def action_demo_env(self):

        """ Example 1: Thực hành tìm hiểu Environment."""

        print("\n========== ENV ==========")

        print("Record hiện tại :", self)
        print("ID :", self.id)

        print()

        print("User hiện tại :", self.env.user.name)
        print("Company :", self.env.company.name)

        print()

        print("Context :")
        print(self.env.context)

        print("=========================\n")
    
        # """ Example 2: Đếm tổng số đồ án. """

        # total = self.env["graduation.project"].search_count([])

        # print("\n========== THỐNG KÊ ==========")
        # print("Tổng số đồ án:", total)
        # print("==============================\n")

        # """ Example 3: Liệt kê toàn bộ đồ án. """

        # projects = self.env["graduation.project"].search([])

        # print("\n========== DANH SÁCH ==========")

        # for project in projects:

        #     print(
        #         project.code,
        #         project.name,
        #         project.state,
        # )

        # print("==============================\n")

        # """ Example 4: Tìm đồ án chưa bảo vệ. """

        # projects = self.env["graduation.project"].search(
        #     [
        #         ("state", "!=", "done")
        #     ]
        # )

        # print("\n========== CHƯA BẢO VỆ ==========")

        # for project in projects:

        #     print(
        #         project.code,
        #         project.name,
        #         project.state,
        #     )

        # print("=================================\n")
        # """ Example 5: Minh họa Context."""

        # print("\n========== CONTEXT ==========")

        # print(self.env.context)

        # print()

        # print("active_model :",
        #     self.env.context.get("active_model"))

        # print("active_id :",
        #     self.env.context.get("active_id"))

        # print("active_ids :",
        #     self.env.context.get("active_ids"))

        # print("=============================\n")



        #Các ví dụ khác tham khảo bên dưới"
        #"""
        #Demo sử dụng Context.
        #"""

        #print("\n========== CONTEXT ==========")

        #print("Context:")

        #print(self.env.context)

        #print("\nCác giá trị thường dùng:")

        #print("Model hiện tại :", self.env.context.get("active_model"))

        #print("ID bản ghi :", self.env.context.get("active_id"))

        #print("Danh sách ID :", self.env.context.get("active_ids"))

        #print("=============================\n")
        #--------------Tách---------------

        #""" Demo sử dụng Environment (env)."""

        #print("\n========== RECORDSET ==========")

        #print("Self :", self)

        #print("Model :", self._name)

        #print("ID :", self.id)

        #print("IDs :", self.ids)

        #print("Số bản ghi :", len(self))

        #print("===============================\n")
        
        #----------------Tách--------------

        #print("\n========== DEMO ENV ==========")

        #print("Recordset :", self)

        #print("Environment :", self.env)

        #print("User :", self.env.user.name)

        #print("User ID :", self.env.uid)

        #print("Company :", self.env.company.name)

        #print("==============================\n")
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
