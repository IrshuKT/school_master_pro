from odoo import models, fields, api

class FinanceHead(models.Model):
    _name = "finance.head"
    _description = "Finance Head"

    name = fields.Char(string="Head Name", required=True)
    type = fields.Selection([
        ("income", "Income"),
        ("expense", "Expense")
    ], string="Type", required=True)

    transaction_ids = fields.One2many("finance.transaction", "head_id", string="Transactions")
    balance = fields.Float(string="Balance", compute="_compute_balance", store=True)

    @api.depends("transaction_ids.signed_amount")
    def _compute_balance(self):
        for rec in self:
            rec.balance = sum(rec.transaction_ids.mapped("signed_amount"))
