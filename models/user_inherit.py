from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    teacher_id = fields.Many2one(
        'teacher.master',
        string="Teacher Profile",
        ondelete="set null"
    )

