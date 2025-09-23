from odoo import models, fields, api
from email.policy import default

from odoo.exceptions import ValidationError


class StudentDocumentsCollection(models.Model):
    _name = 'student.documents.collection'
    _description = 'Student Documents Collection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'


    student_id = fields.Many2one(
        'student.master', string='Student Name',
        required=True, ondelete='cascade'
    )
    collection_date = fields.Datetime(
        'Collection Date',
        default=fields.Datetime.now,tracking=True
    )

    document_line_ids = fields.One2many(
        'student.documents.line',
        'collection_id',
        string='Documents',tracking=True
    )

    state = fields.Selection([
        ('collected', 'Collected'),
        ('partially_returned', 'Partially Returned'),
        ('returned', 'Returned'),
    ], string='Status', compute='_compute_state', store=True)

    is_locked = fields.Boolean(string='Locked', default=False)

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company, readonly=True
    )
    company_logo = fields.Binary(
        string='Company Logo', related='company_id.logo', readonly=True
    )

    @api.depends('document_line_ids.returned_date')
    def _compute_state(self):
        for rec in self:
            lines = rec.document_line_ids
            if lines and all(l.returned_date for l in lines):
                rec.state = 'returned'
            elif any(l.returned_date for l in lines):
                rec.state = 'partially_returned'
            else:
                rec.state = 'collected'

    def action_save(self):
        self.write({'is_locked': True})

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_back(self):
        # Do nothing if the record is new (no ID)
        if not self.id:
            return {'type': 'ir.actions.do_nothing'}
        action = self.env.ref("school_master_pro.student_document_collection_action_window").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }


class StudentDocumentsLine(models.Model):
    _name = 'student.documents.line'
    _description = 'Student Documents Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    collection_id = fields.Many2one(
        'student.documents.collection', string='Collection',
        required=True, ondelete='cascade',tracking=True
    )

    document_type = fields.Selection([
        ('sslc', 'SSLC'),
        ('plus_two', '+2'),
        ('tc', 'TC'),
        ('cc', 'CC'),
        ('other', 'Other'),
    ], string='Document Type', required=True,tracking=True)

    collected_date = fields.Datetime(
        'Collected Date', default=fields.Datetime.now,tracking=True
    )
    returned_date = fields.Datetime('Returned Date',tracking=True)
    note = fields.Text('Remarks',tracking=True)


