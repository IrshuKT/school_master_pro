from odoo import models,fields,api


class FinanceTransaction(models.Model):
    _name = 'finance.transaction'
    _description = 'Cash/Bank Transactions'
    _order = 'date, id'   # Important: ensures proper running balance order

    date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True)
    account_type = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank')
    ], string="Account Type", required=True)
    description = fields.Char(string="Description")
    direction = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], string="Direction", required=True)
    amount = fields.Float(string="Amount", required=True)

    signed_amount = fields.Float(string="Signed Amount", compute="_compute_signed_amount", store=False)
    running_balance = fields.Float(string="Running Balance", compute="_compute_running_balance", store=False)

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    @api.depends('amount', 'direction')
    def _compute_signed_amount(self):
        for rec in self:
            rec.signed_amount = rec.amount if rec.direction == 'in' else -rec.amount

    @api.depends('signed_amount', 'date')
    def _compute_running_balance(self):
        """Compute running balance per account type in batch"""
        # group by account type
        for account_type in ['cash', 'bank']:
            txns = self.search([('account_type', '=', account_type)], order="date, id")
            balance = 0.0
            for txn in txns:
                balance += txn.signed_amount
                txn.running_balance = balance

