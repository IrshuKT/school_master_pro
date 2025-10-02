from odoo import models,fields,api


class TeacherCourseYearBatch(models.Model):
    _name = 'teacher.course.year.batch'
    _description = 'Teacher Course-Year Allocation'

    teacher_id = fields.Many2one('teacher.master', required=True)
    course_id = fields.Many2one('student.class.name', required=True)
    year_id = fields.Many2one('course.year.line', required=True)

    key = fields.Char(compute="_compute_key", store=True, index=True)

    @api.depends('course_id', 'year_id')
    def _compute_key(self):
        for rec in self:
            rec.key = f"{rec.course_id.id}-{rec.year_id.id}" if rec.course_id and rec.year_id else False
