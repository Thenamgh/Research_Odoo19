import base64
import re
from io import BytesIO

from odoo import _, fields, models
from odoo.exceptions import UserError


class ThesisAssignmentImportWizard(models.TransientModel):
    _name = "thesis.assignment.import.wizard"
    _description = "Import danh sách phân công đồ án"

    batch_id = fields.Many2one(
        comodel_name="thesis.batch",
        string="Đợt đồ án",
        required=True,
        ondelete="cascade",
        domain=[("state", "not in", ["done", "cancelled"])],
        help="Tất cả hồ sơ trong file sẽ được đưa vào đợt đồ án này.",
    )

    file_data = fields.Binary(
        string="File Excel",
        required=True,
        attachment=False,
    )

    file_name = fields.Char(
        string="Tên file",
    )

    validated = fields.Boolean(
        string="Đã kiểm tra",
        readonly=True,
    )

    row_count = fields.Integer(
        string="Số sinh viên",
        readonly=True,
    )

    validation_message = fields.Text(
        string="Kết quả kiểm tra",
        readonly=True,
    )

    @staticmethod
    def _normalize_header(value):
        """Chuẩn hóa tên cột để không phụ thuộc chữ hoa và khoảng trắng."""
        if value is None:
            return ""

        return re.sub(
            r"\s+",
            " ",
            str(value).strip().lower(),
        )

    def action_validate_file(self):
        """Kiểm tra định dạng file, tên cột và số dòng dữ liệu."""
        self.ensure_one()

        if not self.file_data:
            raise UserError(_("Vui lòng chọn file Excel cần kiểm tra."))

        if not self.file_name:
            raise UserError(_("Không xác định được tên file Excel."))

        if not self.file_name.lower().endswith(".xlsx"):
            raise UserError(
                _(
                    "File không đúng định dạng.\n"
                    "Hệ thống chỉ chấp nhận file Excel có đuôi .xlsx."
                )
            )

        try:
            from openpyxl import load_workbook
        except ImportError as error:
            raise UserError(
                _(
                    "Máy chủ chưa cài thư viện openpyxl.\n"
                    "Hãy chạy lệnh: python -m pip install openpyxl"
                )
            ) from error

        try:
            file_content = base64.b64decode(self.file_data)
            workbook = load_workbook(
                filename=BytesIO(file_content),
                read_only=True,
                data_only=True,
            )
        except Exception as error:
            raise UserError(
                _(
                    "Không thể đọc file Excel.\n"
                    "File có thể bị hỏng hoặc không phải file .xlsx hợp lệ."
                )
            ) from error

        try:
            worksheet = workbook.active

            header_row = next(
                worksheet.iter_rows(
                    min_row=1,
                    max_row=1,
                    values_only=True,
                ),
                None,
            )

            if not header_row:
                raise UserError(_("File Excel không có dòng tiêu đề."))

            normalized_headers = [
                self._normalize_header(value)
                for value in header_row
            ]

            required_headers = {
                "mã sinh viên",
                "họ và tên",
                "ngày sinh",
                "lớp",
                "tên đồ án",
                "giảng viên hướng dẫn",
                "mã giảng viên",
            }

            actual_headers = {
                header
                for header in normalized_headers
                if header
            }

            missing_headers = sorted(
                required_headers - actual_headers
            )

            if missing_headers:
                raise UserError(
                    _(
                        "File Excel thiếu các cột bắt buộc:\n- %s"
                    )
                    % "\n- ".join(missing_headers)
                )

            student_code_index = normalized_headers.index(
                "mã sinh viên"
            )

            row_count = 0

            for row in worksheet.iter_rows(
                min_row=2,
                values_only=True,
            ):
                if (
                    len(row) > student_code_index
                    and row[student_code_index] not in (None, "")
                ):
                    row_count += 1

            if row_count == 0:
                raise UserError(
                    _(
                        "File có dòng tiêu đề nhưng không có "
                        "dữ liệu sinh viên."
                    )
                )

            self.write(
                {
                    "validated": True,
                    "row_count": row_count,
                    "validation_message": _(
                        "File hợp lệ.\n"
                        "Sheet dữ liệu: %s\n"
                        "Số sinh viên tìm thấy: %s\n"
                        "Đợt đồ án: %s"
                    )
                    % (
                        worksheet.title,
                        row_count,
                        self.batch_id.display_name,
                    ),
                }
            )

        finally:
            workbook.close()

        # Mở lại wizard để hiển thị kết quả kiểm tra
        return {
            "type": "ir.actions.act_window",
            "name": _("Import danh sách phân công"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }