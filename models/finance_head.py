from odoo import models,fields

class FinanceHead(models.Model):
    _name = "finance.head"
    _description = "Finance Head"

    name = fields.Char(string="Head Name", required=True)
    type = fields.Selection([
        ("income", "Income"),
        ("expense", "Expense")
    ], string="Type", required=True)



    def _compute_balance(self):
        for rec in self:
            rec.balance = sum(rec.transaction_ids.mapped("signed_amount"))