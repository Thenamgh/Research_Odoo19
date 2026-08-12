from odoo import models, api
from odoo.exceptions import ValidationError

class GraduationProjectInherit(models.Model):
    _inherit = "graduation.project"

    @api.model_create_multi
    def create(self, vals_list):

        print(">>> INHERIT CREATE ĐÃ ĐƯỢC GỌI")
        print(">>> VALS:", vals_list)

        # Logic mới của module kế thừa
        for vals in vals_list:
            if "test" in vals.get("name", "").lower():
                print(">>> PHÁT HIỆN TỪ TEST")

                raise ValidationError(
                    "Tên đồ án không hợp lệ."
                )

        # Gọi chức năng create() của phần kế thừa phía trước
        return super().create(vals_list)
    def write(self, vals):

        for record in self:

            if record.state == "done" and vals.get("state"):
                raise ValidationError(
                    "Không thể thay đổi trạng thái của đồ án đã bảo vệ."
                )

        return super().write(vals)
# from odoo import models, api

# class GraduationProjectInherit(models.Model):
#     _inherit = "graduation.project"


    # @api.model_create_multi
    # def create(self, vals_list):
    #     print(">>> INHERIT: BEFORE SUPER")

    #     records = super().create(vals_list)

    #     print(">>> INHERIT: AFTER SUPER")

    #     return records