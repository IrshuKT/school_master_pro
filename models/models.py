from odoo import models, fields, api
from odoo.exceptions import ValidationError

"""
# view created sequence 20
class StudentClassNo(models.Model):
    _name = 'student.class.no'
    _description = 'Student Class'
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(string='Year', required=True)
    course_ids = fields.Many2many('student.class.name','course_year_rel','year_id','course_id',
        string="Courses")

    active = fields.Boolean(string='Active', default=True)
    is_locked = fields.Boolean(string='Locked', default=False)
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

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

    def action_new_year(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Year',
            'res_model': 'student.class.no',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
        }

    def action_cancel(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Classes',
            'res_model': 'student.class.no',
            'view_mode': 'list',
            'view_type': 'list',
            'target': 'current',
        }

    @api.constrains('course_ids')
    def _check_course_year_limit(self):
        for year in self:
            for course in year.course_ids:
                # count how many years are already linked to this course
                linked_years = self.search_count([('course_ids', 'in', course.id)])
                try:
                    duration = int(course.duration or 0)
                except ValueError:
                    duration = 0

                if duration and linked_years > duration:
                    raise ValidationError(
                        f"Course '{course.name}' has a maximum duration of {duration} years.\n"
                        f"You are trying to assign more than {duration} years."
                    )



    # VIEW CREATED IN SETTINGS 10 SEQUENCE
class StudentDivision(models.Model):
    _name = 'student.division'
    _description = 'Student Batch'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Batch Name', compute="_compute_name", store=True)
    start_year = fields.Integer(string="Start Year", required=True)
    end_year = fields.Integer(string="End Year", compute="_compute_end_year", store=True)
    course_id = fields.Many2one('student.class.name', string='Course', required=True)

    is_locked = fields.Boolean(string='Locked', default=False)
    active = fields.Boolean(string='Active', default=True)

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company, readonly=True
    )

    @api.depends('start_year', 'course_id.duration')
    def _compute_end_year(self):
        for rec in self:
            if rec.start_year and rec.course_id and rec.course_id.duration:
                try:
                    duration = int(rec.course_id.duration)
                except ValueError:
                    duration = 0
                rec.end_year = rec.start_year + duration
            else:
                rec.end_year = False

    @api.depends('start_year', 'end_year')
    def _compute_name(self):
        for rec in self:
            if rec.start_year and rec.end_year:
                rec.name = f"{rec.start_year} - {rec.end_year}"
            else:
                rec.name = "Batch"

    @api.constrains('start_year', 'end_year', 'course_id')
    def _check_duration_within_course(self):
        for rec in self:
            if rec.course_id and rec.course_id.duration:
                allowed_end_year = rec.start_year + int(rec.course_id.duration)
                if rec.end_year and rec.end_year > allowed_end_year:
                    raise ValidationError(
                        f"Batch duration exceeds the course limit of {rec.course_id.duration} years.\n"
                        f"Start Year: {rec.start_year}, End Year: {rec.end_year}, "
                        f"Allowed Max End Year: {allowed_end_year}"
                    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

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

    def action_new_batch(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Batch',
            'res_model': 'student.division',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
        }

    def action_cancel(self):
        self.write({'is_locked': False})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'student.division',
            'view_mode': 'tree',
            'target': 'main',
        }
"""

class TeacherDesignation(models.Model):
    _name = 'teacher.designation'
    _description = 'Teachers Designation'
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(string='Teachers Designations')
    is_locked = fields.Boolean(string='Locked', default=False)

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


class ExamName(models.Model):
    _name = 'exam.name'
    _description = 'Exam Name'
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(string='Exam Name')
    is_locked = fields.Boolean(string='Locked', default=False)

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


