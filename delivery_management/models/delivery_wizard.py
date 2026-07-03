# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BulkDeliveryConfirmWizard(models.TransientModel):
    _name = 'bulk.delivery.confirm.wizard'
    _description = 'Bulk Delivery Confirm Wizard'

    delivery_ids = fields.Many2many('delivery.management', string='Deliveries')
    
    def action_confirm_all(self):
        for delivery in self.delivery_ids:
            if delivery.state == 'draft':
                delivery.action_confirm()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('All selected deliveries have been confirmed.'),
                'type': 'success',
                'sticky': False,
            }
        }


class DeliveryExportWizard(models.TransientModel):
    _name = 'delivery.export.wizard'
    _description = 'Export Deliveries'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status')
    
    def action_export_csv(self):
        domain = [
            ('created_date', '>=', f"{self.from_date} 00:00:00"),
            ('created_date', '<=', f"{self.to_date} 23:59:59")
        ]
        
        if self.state:
            domain.append(('state', '=', self.state))
        
        deliveries = self.env['delivery.management'].search(domain)
        
        if not deliveries:
            raise UserError(_('No deliveries found for the selected criteria.'))
        
        # Prepare CSV data
        csv_data = "Reference,Customer,Delivery Date,Status,Total Amount,Driver\n"
        for delivery in deliveries:
            csv_data += f'"{delivery.name}","{delivery.partner_id.name}","{delivery.delivery_date}","{delivery.state}","{delivery.total_amount}","{delivery.driver_name}"\n'
        
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model=delivery.management&field=export_csv&download=true&data={csv_data}",
            'target': 'new',
        }


class DeliveryNotificationWizard(models.TransientModel):
    _name = 'delivery.notification.wizard'
    _description = 'Send Delivery Notification'

    delivery_id = fields.Many2one('delivery.management', string='Delivery', required=True)
    email_to = fields.Char(string='Email To', required=True)
    subject = fields.Char(string='Email Subject', required=True, default='Delivery Notification')
    message = fields.Html(string='Message', required=True)
    
    def action_send_notification(self):
        mail_values = {
            'subject': self.subject,
            'body_html': self.message,
            'email_to': self.email_to,
        }
        
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Notification email has been sent.'),
                'type': 'success',
                'sticky': False,
            }
        }
