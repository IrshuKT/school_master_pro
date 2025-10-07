from odoo import models,fields,api


class FinanceVoucher(models.Model):
    _name = "finance.voucher"
    _description = "Accounting Voucher"
    _order = "date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(string="Voucher No.", readonly=True, default="New")
    date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True)
    is_locked = fields.Boolean(string='Locked', default=False)

    voucher_type = fields.Selection([
        ("receipt", "Receipt"),
        ("payment", "Payment"),
    ], string="Voucher Type", required=True ,)

    direction = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], string="Direction", required=True, default='in')

    account_type = fields.Selection([
        ("cash", "Cash"),
        ("bank", "Bank"),
    ], string="Account Type", required=True)

    head_id = fields.Many2one(
        "finance.head",
        string="Head / Account",required=True,help="E.g. Student Fees, Donation, Salary, Vendor Payment")

    partner_id = fields.Char(string="Party / Source", required=True)
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount", required=True)

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
    ], string="Status", default="draft", tracking=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('student.fee.receipt') or 'New'

        records = super().create(vals_list)
        return records

    def action_save(self):
        for rec in self:
            self.write({'is_locked': True})

            txn_vals = {
                "date": rec.date,
                "account_type": rec.account_type,
                "head_id": rec.head_id.id,
                "amount": rec.amount,
                "direction": "in" if rec.voucher_type == "receipt" else "out",
                "description": f"{rec.voucher_type.title()} - {rec.head_id.name} ({rec.partner_id})",
                "ref_model": "finance.voucher",
                "ref_id": rec.id,
            }

            existing_txn = self.env['finance.transaction'].search([
                ('ref_model', '=', 'finance.voucher'),
                ('ref_id', '=', rec.id)
            ], limit=1)

            if existing_txn:
                existing_txn.write(txn_vals)
            else:
                self.env['finance.transaction'].create(txn_vals)

            rec.state = "confirmed"

        # Trigger UI refresh for cash/bank book
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    # def action_save(self):
    #     for rec in self:
    #         self.write({'is_locked': True})
    #         self.env["finance.transaction"].create({
    #             "date": rec.date,
    #             "account_type": rec.account_type,
    #             "head_id": rec.head_id.id,  # 🔥 Add this line
    #             "description": f"{rec.voucher_type.title()} - {rec.head_id.name} ({rec.partner_id})",
    #             "amount": rec.amount,
    #             "direction": "in" if rec.voucher_type == "receipt" else "out",            })
    #
    #         rec.state = "confirmed"

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_back(self):
        # Do nothing if the record is new (no ID)
        if not self.id:
            return {'type': 'ir.actions.do_nothing'}
        action = self.env.ref("school_master_pro.action_finance_voucher").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }



