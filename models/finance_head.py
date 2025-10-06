from odoo import models, fields, api

class FinanceHead(models.Model):
    _name = "finance.head"
    _description = "Finance Head"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Head Name", required=True)
    type = fields.Selection([
        ("income", "Income"),
        ("expense", "Expense")
    ], string="Type", required=True)

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    is_locked = fields.Boolean(string='Locked', default=False)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='confirmed', tracking=True)

    def action_save(self):
        # Use single write operation for better performance
        self.write({
            'is_locked': True,
            'state': 'confirmed'
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_back(self):
        # Do nothing if the record is new (no ID)
        if not self.id:
            return {'type': 'ir.actions.do_nothing'}
        action = self.env.ref("school_master_pro.action_student_invoice").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }

