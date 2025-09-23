from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class StudentMasterOne(models.Model):
    _inherit = 'student.master'




class StudentFeeInvoice(models.Model):
    _name = 'student.fee.invoice'
    _description = 'Student Fee Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'description'


    student_id = fields.Many2one('student.master', string="Student", required=True, ondelete='cascade')
    course_id = fields.Many2one('student.class.name', string="Course", readonly=True)
    year_id = fields.Many2one(
        'course.year.line',
        string="Year",
        domain="[('course_id', '=', course_id)]",  # 🔑 Only years of selected course
        required=True
    )
    original_amount = fields.Float(string="Original Amount", readonly=True)
    discount_amount = fields.Float(string="Concession", readonly=True)
    amount = fields.Float(string="Invoice Amount", required=True, tracking=True)
    description = fields.Char(string="Description", required=True)
    invoice_date = fields.Date(string="Invoice Date", default=fields.Date.today, required=True)
    is_locked = fields.Boolean(string='Locked', default=False)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='confirmed', tracking=True)

    invoice_type = fields.Selection([
        ('admission', 'Admission Fee'),
        ('term_one', 'Term One Fee'),
        ('term_two', 'Term Two Fee'),
        ('term_three', 'Term Three Fee'),
    ], string='Invoice Type', tracking=True)

    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)


    @api.onchange('student_id')
    def _onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.course_id = rec.student_id.student_class_name.id
                rec.year_id = rec.student_id.student_class.id
            else:
                rec.course_id = False
                rec.year_id = False

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure original_amount is set on creation"""
        for vals in vals_list:
            # if original_amount is empty → set it equal to entered amount
            if not vals.get("original_amount"):
                vals["original_amount"] = vals.get("amount", 0.0)
        return super().create(vals_list)
    """
    # Add SQL constraints to prevent duplicates
    _sql_constraints = [
        ('unique_admission_fee_per_student', 
         "UNIQUE(student_id, invoice_type) WHERE invoice_type = 'admission'",
         'Only one admission fee invoice allowed per student!'),
        
        ('unique_term_one_fee_per_student', 
         "UNIQUE(student_id, invoice_type) WHERE invoice_type = 'term_one'",
         'Only one term one fee invoice allowed per student!'),
    ]
    """
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
        # Do nothing if the record is new (no ID)
        if not self.id:
            return {'type': 'ir.actions.do_nothing'}
        action = self.env.ref("school_master_pro.action_student_invoice").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }

    @api.model
    def generate_next_term_invoices(self):
        """Cron job: Generate Term 2 and Term 3 invoices automatically"""
        students = self.env['student.master'].search([])
        invoice_count = 0

        for student in students:
            course = student.course_id
            if not course:
                continue

            # ✅ Term 2 (after Term 1)
            term1_invoice = self.search([
                ('student_id', '=', student.id),
                ('invoice_type', '=', 'term_one'),
                ('state', '=', 'confirmed')
            ], order='invoice_date desc', limit=1)

            if term1_invoice and course.term_two_fee > 0:
                #due_date = term1_invoice.invoice_date + timedelta(days=90)
                due_date = term1_invoice.invoice_date + timedelta(minutes=5)  # ⏱ testing
                if fields.Date.today() >= due_date:
                    exists = self.search([
                        ('student_id', '=', student.id),
                        ('invoice_type', '=', 'term_two')
                    ], limit=1)
                    if not exists:
                        self.create({
                            'student_id': student.id,
                            'course_id': course.id,
                            'year_id': student.year_id.id if student.year_id else False,
                            'invoice_date': fields.Date.today(),
                            'description': f"Term 2 Fee - {course.name}",
                            'amount': course.term_two_fee,
                            'invoice_type': 'term_two',
                            'state': 'confirmed',
                            'company_id': self.env.company.id,
                        })
                        invoice_count += 1

            # ✅ Term 3 (after Term 2)
            term2_invoice = self.search([
                ('student_id', '=', student.id),
                ('invoice_type', '=', 'term_two'),
                ('state', '=', 'confirmed')
            ], order='invoice_date desc', limit=1)

            if term2_invoice and course.term_three_fee > 0:
                #due_date = term1_invoice.invoice_date + timedelta(days=90)
                due_date = term2_invoice.invoice_date + timedelta(minutes=5)  # ⏱ testing
                if fields.Date.today() >= due_date:
                    exists = self.search([
                        ('student_id', '=', student.id),
                        ('invoice_type', '=', 'term_three')
                    ], limit=1)
                    if not exists:
                        self.create({
                            'student_id': student.id,
                            'course_id': course.id,
                            'year_id': student.year_id.id if student.year_id else False,
                            'invoice_date': fields.Date.today(),
                            'description': f"Term 3 Fee - {course.name}",
                            'amount': course.term_three_fee,
                            'invoice_type': 'term_three',
                            'state': 'confirmed',
                            'company_id': self.env.company.id,
                        })
                        invoice_count += 1

        _logger.info("✅ Cron generated %s new term invoices", invoice_count)
        return invoice_count
