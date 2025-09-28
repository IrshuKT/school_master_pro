from odoo import models, fields, api


class FinanceTransaction(models.Model):
    _name = 'finance.transaction'
    _description = 'Cash/Bank Transactions'
    _order = 'date, id'

    date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True)
    account_type = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank')
    ], string="Account Type", required=True)
    description = fields.Char(string="Description")

    head_id = fields.Many2one("finance.head", string="Finance Head", required=True)

    direction = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], string="Direction", required=True)
    amount = fields.Float(string="Amount", required=True)

    signed_amount = fields.Float(string="Signed Amount", compute="_compute_signed_amount", store=True)
    running_balance = fields.Float(string="Running Balance", compute="_compute_running_balance", store=False)

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    @api.depends('amount', 'direction')
    def _compute_signed_amount(self):
        for rec in self:
            rec.signed_amount = rec.amount if rec.direction == 'in' else -rec.amount

    @api.depends('signed_amount', 'date', 'account_type')
    def _compute_running_balance(self):
        # Initialize all with 0 to avoid ValueError on new records
        for rec in self:
            rec.running_balance = 0.0

        # Compute only on saved records
        all_txns = self.search([], order="account_type, date, id")
        balances = {'cash': 0.0, 'bank': 0.0}
        for txn in all_txns:
            balances[txn.account_type] += txn.signed_amount
            txn.running_balance = balances[txn.account_type]

