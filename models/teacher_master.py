from datetime import date
from email.policy import default

from dateutil.relativedelta import relativedelta

from odoo import models,fields,api

class TeacherMaster(models.Model):
    _name = 'teacher.master'
    _description = 'Student Class Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string='Teacher Name', required=True)
    gender= fields.Selection([('male','Male'),('female','Female')],string='Gender',default='male')
    doj = fields.Date('Date of Joining')
    year_of_service = fields.Char(string='Servicing Years',compute='_compute_year_of_service',store=True)
    active = fields.Boolean('Active',default=True)
    contact_no = fields.Char(string='Contact No')
    emergency_contact = fields.Char(string='Emergency Contact')
    address = fields.Text('Address')
    designation_id = fields.Many2one('teacher.designation',string='Designation')
    is_locked = fields.Boolean(string='Locked', default=False)

    user_id = fields.Many2one('res.users',string="Related User",ondelete="set null",index=True,tracking=True)
    course_year_batch_ids = fields.One2many('teacher.course.year.batch',
        'teacher_id',string="Allocated Course-Year")

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

    def get_allocated_course_years(self):
        self.ensure_one()
        return [(line.course_id.id, line.year_id.id) for line in self.course_year_batch_ids]

    _sql_constraints = [
        ('unique_user_teacher', 'unique(user_id)', 'Each user can only have one teacher profile.')
    ]

    @api.depends('doj')
    def _compute_year_of_service(self):
        today = date.today()
        for record in self:
            if record.doj:
                delta = relativedelta(today, record.doj)
                record.year_of_service = f"{delta.years}y {delta.months}m {delta.days}d"
            else:
                record.year_of_service = "0y 0m 0d"

    def action_save(self):
        self.write({'is_locked': True})
        for rec in self:
            rec.state = 'confirmed'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_back(self):
        action = self.env.ref("school_master_pro.teacher_master_action_window").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }

    def write(self, vals):
        # If state is being set to draft, always unlock
        if 'state' in vals and vals['state'] == 'draft':
            vals['is_locked'] = False

        # capture old user ids so we can clear their teacher_id if unlinked/changed
        old_users = {rec.id: rec.user_id.id for rec in self}
        res = super().write(vals)

        try:
            teacher_group = self.env.ref('school_master_pro.group_teacher_user')
        except Exception:
            teacher_group = False

        for rec in self:
            old_uid = old_users.get(rec.id)
            new_uid = rec.user_id.id if rec.user_id else False

            # if user changed, clear old user's teacher_id and remove teacher group
            if old_uid and old_uid != new_uid:
                u = self.env['res.users'].browse(old_uid)
                u.sudo().write({'teacher_id': False})
                if teacher_group:
                    u.sudo().write({'groups_id': [(3, teacher_group.id)]})

            # ensure new user points back to teacher and has teacher group
            if new_uid:
                rec.user_id.sudo().write({'teacher_id': rec.id})
                if teacher_group:
                    rec.user_id.sudo().write({'groups_id': [(4, teacher_group.id)]})

        return res




    #student_ids = fields.One2many('student.master','teacher_id',string="Assigned Students")

    # #course_ids = fields.Many2many(
    #     'student.class.name',
    #     'teacher_course_rel','teacher_id','course_id',string="Allocated Courses")
    #
    # year_ids = fields.Many2many(
    #     'course.year.line',
    #     'teacher_year_rel','teacher_id','year_id',string="Allocated Years")

    # batch_ids = fields.Many2many(
    #     'student.division','teacher_batch_rel','teacher_id','batch_id',string="Allocated Batches",tracking=True)
    #
    # courses = fields.Many2one('student.class.name',string='Course')
    # std = fields.Many2many('student.class.no',string='Year')






