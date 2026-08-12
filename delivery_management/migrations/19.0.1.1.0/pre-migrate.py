from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    Chuyển dữ liệu sinh viên hiện có sang Delegation inheritance.

    Quy trình:
    1. Tạo cột partner_id nếu chưa tồn tại.
    2. Tạo hoặc tái sử dụng res.partner theo mã sinh viên.
    3. Gắn partner_id vào thesis.student.
    4. Chuyển thesis.assignment.student_id từ res.partner
       sang thesis.student.
    5. Không xóa các cột name, email, phone cũ để dự phòng.
    """

    # Không cho phép mã sinh viên bị trùng vì sẽ không thể
    # ánh xạ chính xác sang res.partner.
    cr.execute(
        """
        SELECT LOWER(BTRIM(student_code)), ARRAY_AGG(id ORDER BY id)
        FROM thesis_student
        WHERE student_code IS NOT NULL
          AND BTRIM(student_code) != ''
        GROUP BY LOWER(BTRIM(student_code))
        HAVING COUNT(*) > 1
        """
    )
    duplicate_codes = cr.fetchall()

    if duplicate_codes:
        raise RuntimeError(
            "Không thể chuyển đổi Delegation inheritance vì có "
            "mã sinh viên trùng: %s"
            % duplicate_codes[:20]
        )

    # Tạo cột liên kết trước khi Odoo khởi tạo lại model.
    cr.execute(
        """
        ALTER TABLE thesis_student
        ADD COLUMN IF NOT EXISTS partner_id INTEGER
        """
    )

    cr.execute(
        """
        SELECT
            id,
            name,
            email,
            phone,
            student_code
        FROM thesis_student
        WHERE partner_id IS NULL
        ORDER BY id
        """
    )
    students = cr.fetchall()

    env = api.Environment(cr, SUPERUSER_ID, {})
    Partner = env["res.partner"].with_context(active_test=False)

    for (
        student_id,
        student_name,
        student_email,
        student_phone,
        student_code,
    ) in students:
        existing_partners = Partner.browse()

        if student_code:
            existing_partners = Partner.search(
                [("ref", "=ilike", student_code)],
                limit=2,
            )

        if len(existing_partners) > 1:
            raise RuntimeError(
                "Có nhiều res.partner cùng mã sinh viên %s. "
                "Cần xử lý trùng trước khi nâng cấp."
                % student_code
            )

        if existing_partners:
            partner = existing_partners[0]
        else:
            partner = Partner.create(
                {
                    "name": (
                        student_name
                        or student_code
                        or "Sinh viên %s" % student_id
                    ),
                    "email": student_email or False,
                    "phone": student_phone or False,
                    "ref": student_code or False,
                    "company_type": "person",
                    "type": "contact",
                }
            )

        cr.execute(
            """
            UPDATE thesis_student
            SET partner_id = %s
            WHERE id = %s
            """,
            (partner.id, student_id),
        )

    env.flush_all()

    # Mọi sinh viên phải có partner sau khi chuyển đổi.
    cr.execute(
        """
        ALTER TABLE thesis_student
        ALTER COLUMN partner_id SET NOT NULL
        """
    )

    # Kiểm tra các bản ghi giao nhận cũ có thể ánh xạ hay không.
    cr.execute(
        """
        SELECT assignment.id, assignment.student_id
        FROM thesis_assignment AS assignment
        LEFT JOIN thesis_student AS student
            ON student.partner_id = assignment.student_id
        WHERE student.id IS NULL
        """
    )
    unmapped_assignments = cr.fetchall()

    if unmapped_assignments:
        raise RuntimeError(
            "Không thể xác định thesis.student tương ứng cho "
            "các thesis.assignment: %s"
            % unmapped_assignments[:20]
        )

    # Xóa khóa ngoại cũ đang trỏ tới res.partner.
    cr.execute(
        """
        ALTER TABLE thesis_assignment
        DROP CONSTRAINT IF EXISTS
        thesis_assignment_student_id_fkey
        """
    )

    # Chuyển giá trị partner ID thành thesis.student ID.
    cr.execute(
        """
        UPDATE thesis_assignment AS assignment
        SET student_id = student.id
        FROM thesis_student AS student
        WHERE assignment.student_id = student.partner_id
        """
    )