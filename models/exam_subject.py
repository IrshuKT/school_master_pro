from odoo import models,fields,api


class ExamSubject(models.Model):
    _name = 'exam.subject'
    _description = 'Exam Subject'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    course_id = fields.Many2one('student.class.name', string="Course", required=True, tracking=True)
    year_id = fields.Many2one(
        'course.year.line', string="Year", domain="[('course_id', '=', course_id)]", required=True, tracking=True)
    name = fields.Char(string='Subject Name',required=True,tracking=True)
    is_locked = fields.Boolean(string='Locked', default=False)
    active = fields.Boolean(string='Active', default=True)

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',default=lambda self: self.env.company, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

    def action_save(self):
        self.write({'is_locked': True})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_edit(self):
        self.write({'is_locked': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_back(self):
        if not self.id:
            return {'type': 'ir.actions.do_nothing'}
        action = self.env.ref("school_master_pro.action_course_subject").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }

