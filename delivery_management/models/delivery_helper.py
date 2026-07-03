# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DeliveryHelper(models.Model):
    _name = 'delivery.helper'
    _description = 'Delivery Helper Functions'

    @staticmethod
    def validate_delivery_date(delivery_date):
        """Validate delivery date"""
        if not delivery_date:
            raise ValidationError(_('Delivery date is required'))
        return True

    @staticmethod
    def validate_address(address):
        """Validate delivery address"""
        if not address or len(address.strip()) < 5:
            raise ValidationError(_('Please provide a valid delivery address (at least 5 characters)'))
        return True

    @staticmethod
    def validate_customer(partner_id):
        """Validate customer information"""
        if not partner_id:
            raise ValidationError(_('Customer is required'))
        return True


class DeliveryNotification(models.Model):
    _name = 'delivery.notification'
    _description = 'Delivery Notifications'

    delivery_id = fields.Many2one('delivery.management', string='Delivery', required=True, ondelete='cascade')
    notification_type = fields.Selection([
        ('order_received', 'Order Received'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], string='Notification Type', required=True)
    
    message = fields.Text(string='Message')
    sent_date = fields.Datetime(string='Sent Date', default=fields.Datetime.now)
    
    def send_notification(self):
        """Send notification to customer"""
        if not self.delivery_id.partner_id.email:
            raise ValidationError(_('Customer email is not available'))
        
        email_values = {
            'subject': f'Delivery Status Update - {self.delivery_id.name}',
            'email_to': self.delivery_id.partner_id.email,
            'body_html': self.message or f'Your delivery is {self.get_notification_type_label()}',
        }
        
        mail = self.env['mail.mail'].create(email_values)
        mail.send()
        
        return True
    
    def get_notification_type_label(self):
        """Get notification type label"""
        labels = {
            'order_received': 'received and is being processed',
            'in_transit': 'in transit to your location',
            'out_for_delivery': 'out for delivery today',
            'delivered': 'has been delivered',
            'failed': 'delivery was not successful',
        }
        return labels.get(self.notification_type, 'status updated')


class DeliveryTracking(models.Model):
    _name = 'delivery.tracking'
    _description = 'Delivery Tracking'

    delivery_id = fields.Many2one('delivery.management', string='Delivery', required=True, ondelete='cascade')
    
    tracking_number = fields.Char(string='Tracking Number', unique=True)
    location = fields.Char(string='Current Location')
    latitude = fields.Float(string='Latitude')
    longitude = fields.Float(string='Longitude')
    
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ], string='Status', default='pending')
    
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    
    notes = fields.Text(string='Notes')
