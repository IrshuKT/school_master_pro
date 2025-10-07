from odoo import models, fields, api

class TeacherProfileUpdateWizard(models.TransientModel):
    _name = 'teacher.profile.update.wizard'
    _description = 'Teacher Profile Update Wizard'

    designation_id = fields.Many2one('teacher.designation', string="Designation", required=True)
    course_id = fields.Many2one('student.class.name', string="Course", )
    year_id = fields.Many2one('course.year.line', string="Year")

    def action_update_profile(self):
        teacher = self.env.user.teacher_id
        if teacher:
            teacher.write({
                'designation_id': self.designation_id.id,
                'course_year_batch_ids': [(0, 0, {
                    'course_id': self.course_id.id,
                    'year_id': self.year_id.id
                })],
            })
        return {'type': 'ir.actions.act_window_close'}