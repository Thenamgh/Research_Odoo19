from odoo import api, fields, models
from datetime import datetime


class DeliveryManagement(models.Model):
    _name = "delivery.management"
    _description = "Delivery Management"
    _order = "id desc"

    name = fields.Char(
        string="Delivery Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: "NEW",
    )

    delivery_date = fields.Datetime(
        string="Delivery Date", required=True, default=fields.Datetime.now
    )
    expected_delivery_date = fields.Datetime(string="Expected Delivery Date")

    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    partner_phone = fields.Char(
        related="partner_id.phone", string="Customer Phone", readonly=True
    )
    partner_email = fields.Char(
        related="partner_id.email", string="Customer Email", readonly=True
    )

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")

    delivery_lines = fields.One2many(
        "delivery.line", "delivery_id", string="Delivery Items"
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    delivery_address = fields.Text(string="Delivery Address", required=True)
    description = fields.Text(string="Notes")

    total_quantity = fields.Float(
        string="Total Quantity", compute="_compute_totals", store=True
    )
    total_amount = fields.Float(
        string="Total Amount", compute="_compute_totals", store=True
    )

    driver_name = fields.Char(string="Driver Name")
    vehicle_plate = fields.Char(string="Vehicle Plate")

    created_by = fields.Many2one(
        "res.users",
        string="Created By",
        default=lambda self: self.env.user,
        readonly=True,
    )
    created_date = fields.Datetime(
        string="Created Date", default=fields.Datetime.now, readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "NEW") == "NEW":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "delivery.management"
                ) or "DM/" + datetime.now().strftime("%Y%m%d%H%M%S")
        return super().create(vals_list)

    @api.depends("delivery_lines.quantity", "delivery_lines.amount")
    def _compute_totals(self):
        for record in self:
            record.total_quantity = sum(line.quantity for line in record.delivery_lines)
            record.total_amount = sum(line.amount for line in record.delivery_lines)

    def action_confirm(self):
        self.write({"state": "confirmed"})
        return True

    def action_start_delivery(self):
        self.write({"state": "in_progress"})
        return True

    def action_complete(self):
        self.write({"state": "completed"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True


class DeliveryLine(models.Model):
    _name = "delivery.line"
    _description = "Delivery Line Items"

    delivery_id = fields.Many2one(
        "delivery.management", string="Delivery", required=True, ondelete="cascade"
    )

    product_id = fields.Many2one("product.product", string="Product", required=True)
    product_code = fields.Char(
        related="product_id.default_code", string="Product Code", readonly=True
    )

    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    uom_id = fields.Many2one(
        "uom.uom", string="Unit of Measure", related="product_id.uom_id", readonly=True
    )

    unit_price = fields.Float(string="Unit Price")
    amount = fields.Float(string="Amount", compute="_compute_amount", store=True)

    description = fields.Text(string="Description")
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("delivered", "Delivered"),
            ("partial", "Partial"),
        ],
        string="Item Status",
        default="pending",
    )

    @api.depends("quantity", "unit_price")
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.unit_price


class DeliveryReceiver(models.Model):
    _name = "delivery.receiver"
    _description = "Delivery Receiver"

    delivery_id = fields.Many2one(
        "delivery.management", string="Delivery", required=True, ondelete="cascade"
    )

    receiver_name = fields.Char(string="Receiver Name", required=True)
    receiver_phone = fields.Char(string="Receiver Phone")
    receiver_email = fields.Char(string="Receiver Email")

    signature_date = fields.Datetime(string="Signature Date")
    signature = fields.Binary(string="Signature")

    notes = fields.Text(string="Notes")
