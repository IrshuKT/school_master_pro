# from odoo import models,fields
#
#
# class FeeStructure(models.Model):
#     _name = 'fee.structure'
#     _description = 'Fee Structure Details'
#     _rec_name = 'course_id'
#
#     course_id = fields.Many2one('student.class.name',string='Course Name')
#     quarter_fee = fields.Float('Quarter Fee')
#     is_locked = fields.Boolean(string="Locked", default=False)