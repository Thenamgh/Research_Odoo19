# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta


class DeliveryStatistics(models.Model):
    _name = 'delivery.statistics'
    _description = 'Delivery Statistics'

    name = fields.Char(string='Statistics Name')
    period = fields.Selection([
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
    ], string='Period', default='today')
    
    total_deliveries = fields.Integer(string='Total Deliveries', compute='_compute_statistics')
    completed_deliveries = fields.Integer(string='Completed Deliveries', compute='_compute_statistics')
    pending_deliveries = fields.Integer(string='Pending Deliveries', compute='_compute_statistics')
    total_amount = fields.Float(string='Total Amount', compute='_compute_statistics')
    
    @api.depends('period')
    def _compute_statistics(self):
        for record in self:
            today = fields.Datetime.now()
            
            if record.period == 'today':
                domain = [('created_date', '>=', today.replace(hour=0, minute=0, second=0))]
            elif record.period == 'week':
                start = today - timedelta(days=today.weekday())
                domain = [('created_date', '>=', start.replace(hour=0, minute=0, second=0))]
            else:  # month
                domain = [('created_date', '>=', today.replace(day=1, hour=0, minute=0, second=0))]
            
            deliveries = self.env['delivery.management'].search(domain)
            record.total_deliveries = len(deliveries)
            record.completed_deliveries = len(deliveries.filtered(lambda d: d.state == 'completed'))
            record.pending_deliveries = len(deliveries.filtered(lambda d: d.state in ['draft', 'confirmed']))
            record.total_amount = sum(d.total_amount for d in deliveries)


class DeliveryReport(models.Model):
    _name = 'delivery.report'
    _description = 'Delivery Report'
    _auto = False

    delivery_id = fields.Many2one('delivery.management', string='Delivery')
    partner_id = fields.Many2one('res.partner', string='Customer')
    delivery_date = fields.Datetime(string='Delivery Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status')
    total_amount = fields.Float(string='Total Amount')
    total_quantity = fields.Float(string='Total Quantity')
    driver_name = fields.Char(string='Driver')

    def init(self):
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW delivery_report AS
            SELECT
                d.id,
                d.id as delivery_id,
                d.partner_id,
                d.delivery_date,
                d.state,
                d.total_amount,
                d.total_quantity,
                d.driver_name
            FROM delivery_management d
        ''')
