from odoo import models, fields, api


class FinanceTransaction(models.Model):
    _name = 'finance.transaction'
    _description = 'Cash/Bank Transactions'


    # --- Basic Fields ---
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
    ], string="Direction", required=True, default='in')
    amount = fields.Float(string="Amount", required=True)

    # --- Computed Fields ---
    signed_amount = fields.Float(string="Signed Amount", compute="_compute_signed_amount", store=True)
    running_balance = fields.Float(string="Running Balance", compute="_compute_running_balance", store=False)

    # --- Company Fields ---
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    # --- Reference to source documents to prevent duplicates ---
    ref_model = fields.Char(string="Source Model")
    ref_id = fields.Integer(string="Source ID")

    # --- Compute signed_amount ---
    @api.depends('amount', 'direction')
    def _compute_signed_amount(self):
        for rec in self:
            rec.signed_amount = rec.amount if rec.direction == 'in' else -rec.amount

    # --- Compute running balance per account type ---
    @api.depends('signed_amount', 'date', 'account_type')
    def _compute_running_balance(self):
        for account in ['cash', 'bank']:
            txns = self.search([('account_type', '=', account)], order='date, id')
            balance = 0.0
            for txn in txns:
                balance += txn.signed_amount
                txn.running_balance = balance

    # --- Optional: override create to enforce unique ref_model/ref_id ---
    @api.model_create_multi
    def create(self, vals_list):
        new_records = []
        for vals in vals_list:
            existing = None
            if vals.get('ref_model') and vals.get('ref_id'):
                existing = self.search([
                    ('ref_model', '=', vals['ref_model']),
                    ('ref_id', '=', vals['ref_id'])
                ], limit=1)
            if existing:
                existing.write({
                    'date': vals.get('date', existing.date),
                    'account_type': vals.get('account_type', existing.account_type),
                    'head_id': vals.get('head_id', existing.head_id.id),
                    'description': vals.get('description', existing.description),
                    'amount': vals.get('amount', existing.amount),
                    'direction': vals.get('direction', existing.direction),
                })
                new_records += existing
            else:
                rec = super(FinanceTransaction, self).create([vals])
                new_records += rec
        return self.browse([r.id for r in new_records])
