

from odoo import models,fields,api


class TransportMonthlyFee(models.Model):
    _name = 'transport.monthly.fee'
    _description = 'Monthly Transport Fee'
    _order = 'month desc'

    transport_id = fields.Many2one('student.transportation', required=True)
    #student_id = fields.Many2one(related='transport_id.student_id', store=True)
    student_id = fields.Many2one('student.master',string='Student Name')
    month = fields.Date('For Month', required=True)
    amount = fields.Float('Amount', required=True)
    due_date = fields.Date('Due Date')
    payment_date = fields.Date('Payment Date')
    state = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('late', 'Late Payment')
    ], default='unpaid', string='Status')
    notes = fields.Text('Payment Notes')

    def mark_as_paid(self):
        self.write({
            'state': 'paid',
            'payment_date': fields.Date.today()
        })

    @api.model
    def _check_late_payments(self):
        """Cron job to check for late payments"""
        today = fields.Date.today()
        unpaid_fees = self.search([
            ('state', '=', 'unpaid'),
            ('due_date', '<', today)
        ])
        unpaid_fees.write({'state': 'late'})