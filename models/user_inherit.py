from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    teacher_id = fields.Many2one(
        'teacher.master',
        string="Teacher Profile",
        ondelete="set null"
    )

