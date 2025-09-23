import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
import dateutil.utils
from odoo import models, fields, api

class StudentFee(models.Model):
    _name = 'student.academic'
    _description = 'Student Academic Fee Details'

    name = fields.Char(string='Student Name')
    receipt_date = fields.Date(string='Date', default=dateutil.utils.today())
    course = fields.Char(string='Course')
    year = fields.Char(string='Year')
    division = fields.Char(string='Batch')
    student_id = fields.Many2one('student.master')
    active = fields.Boolean(string='Active', default=True)

    total_fees_accumulated = fields.Float(string='Total Fees Accumulated', default=0.00, readonly=True)
    current_balance = fields.Float(string='Current Balance', compute='_compute_current_balance', store=True)
    last_fee_addition = fields.Datetime(string='Last Fee Addition', readonly=True)
    is_locked = fields.Boolean(string='Locked', default=False)

    initial_course_fee = fields.Float(string='Initial Course Fee', readonly=True)
    initial_admission_fee = fields.Float(string='Initial Admission Fee', readonly=True)

    total_fees_paid = fields.Float(string='Total Fees Paid', default=0.0, readonly=True)
    fee_receipt_ids = fields.One2many('student.fee.receipt', 'academic_id', string='Fee Receipts')

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



    # -----------------------------------------------------
    # COMPUTE & ONCHANGE
    # -----------------------------------------------------
    @api.depends('total_fees_accumulated', 'total_fees_paid')
    def _compute_current_balance(self):
        for record in self:
            record.current_balance = record.total_fees_accumulated - record.total_fees_paid

    @api.onchange('student_id')
    def _onchange_student_id(self):
        """Update course, year and fees when student is selected"""
        self.course = False
        self.year = False
        self.division = False
        self.initial_course_fee = 0.0
        self.initial_admission_fee = 0.0

        if self.student_id:
            self.course = self.student_id.student_class_name.name if self.student_id.student_class_name else False
            self.year = self.student_id.student_class.name if self.student_id.student_class else False
            # self.division = self.student_id.student_division.name if self.student_id.student_division else False

            if self.student_id.student_class_name:
                course = self.student_id.student_class_name
                self.initial_course_fee = course.quarter_fee
                self.initial_admission_fee = course.admission_fee
                self.total_fees_accumulated = course.quarter_fee + course.admission_fee
                self.current_balance = self.total_fees_accumulated

    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------
    @api.model_create_multi
    def create(self, vals):
        record = super(StudentFee, self).create(vals)

        if record.student_id and record.student_id.student_class_name:
            course = record.student_id.student_class_name
            record.initial_course_fee = course.quarter_fee
            record.initial_admission_fee = course.admission_fee
            record.total_fees_accumulated = course.quarter_fee + course.admission_fee
            record.current_balance = record.total_fees_accumulated

            record.student_id.write({
                'academic_id': record.id,
                'total_fees_accumulated': record.total_fees_accumulated
            })

        return record

    # -----------------------------------------------------
    # WRITE (NEW)
    # -----------------------------------------------------
    def write(self, vals):
        for record in self:
            # If student or course changed, recompute fees and put them into vals
            if ('student_id' in vals or 'course' in vals or 'year' in vals):
                if record.student_id and record.student_id.student_class_name:
                    course = record.student_id.student_class_name
                    vals.update({
                        'initial_course_fee': course.quarter_fee,
                        'initial_admission_fee': course.admission_fee,
                        'total_fees_accumulated': course.quarter_fee + course.admission_fee,
                        'current_balance': (course.quarter_fee + course.admission_fee) - record.total_fees_paid,
                    })

                    # Keep student.master synced
                    record.student_id.write({
                        'total_fees_accumulated': course.quarter_fee + course.admission_fee,
                    })

        # 🔑 Important: only call once here
        return super(StudentFee, self).write(vals)

    # -----------------------------------------------------
    # METHODS
    # -----------------------------------------------------
    def add_quarterly_fee(self, total_fees_paid):
        for record in self:
            if record.is_locked:
                raise UserError("Cannot update fees. The academic record is locked.")
            record.total_fees_accumulated += total_fees_paid
            record.last_fee_addition = fields.Datetime.now()
            _logger.info(f"Added quarterly fee {total_fees_paid} to {record.name}. New total: {record.total_fees_accumulated}")

    def add_fee_payment(self, amount):
        for record in self:
            if amount <= 0:
                raise UserError("Payment amount must be greater than zero.")
            if amount > record.current_balance:
                raise UserError("Payment amount cannot exceed current balance.")
            record.write({'total_fees_paid': record.total_fees_paid + amount})
            _logger.info(f"Added payment {amount} for {record.name}. Total paid: {record.total_fees_paid}")
