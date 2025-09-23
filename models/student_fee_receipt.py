from odoo import models,fields,api
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StudentFeeReceipt(models.Model):
    _name = 'student.fee.receipt'
    _description = 'Student Fee Receipts'
    _rec_name = 'student_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Receipt Number',readonly=True,default='New')
    #student_id = fields.Many2one('student.master', string='Student Name')
    student_id = fields.Many2one(
        'student.master',
        string='Student Name',
        domain="[('student_class_name','=',course_id), ('course.year.line','=',year_id)]",
        required=True,tracking=True
    )
    #academic_id = fields.Many2one('student.academic', string='Academic Record', related='student_id.academic_id',
                                  #store=True)
    course_id = fields.Many2one(
        'student.class.name',
        string="Course",
        required=True
    )
    year_id = fields.Many2one(
        'course.year.line',
        string="Year",
        domain="[('course_id', '=', course_id)]",  # 🔑 Only years of selected course
        required=True
    )
    amount = fields.Float(string='Amount', required=True,tracking=True)
    payment_date = fields.Datetime(string='Payment Date', default=fields.Datetime.now)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment')
    ], string='Payment Method', default='cash',tracking=True)
    reference = fields.Char(string='Payment Reference',tracking=True)
    collected_by = fields.Many2one(
        'res.users', string='Collected By', default=lambda self: self.env.user
    )
    is_locked = fields.Boolean(string='Locked', default=False)
    # Add a related field to get the company logo
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    # Ensure company_id exists in the model
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

    receipt_type = fields.Selection([
        ('payment', 'Payment'),
        ('concession', 'Concession'),
    ], string="Receipt Type", default='payment', required=True)

    def action_back(self):
        action = self.env.ref("school_master_pro.action_student_fee_receipt").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('student.fee.receipt') or 'New'

        records = super().create(vals_list)
        return records

    # Locking / Unlocking
    def action_save(self):
        self.write({'is_locked': True})
        for rec in self:
            rec.state = 'confirmed'

            ledger_type = 'cash' if rec.payment_method == 'cash' else 'bank'

            self.env['finance.transaction'].create({
                'date': rec.payment_date,
                'account_type': ledger_type,
                'description': f"Receipt {rec.name} ({rec.student_id.student_name})",
                'amount': rec.amount,
                'direction': 'in',
            })

            _logger.info("Transaction recorded: %s %s %.2f",
                         ledger_type, rec.payment_method, rec.amount)

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}



    # Filter students by selected course and year
    @api.onchange('course_id', 'year_id')
    def _onchange_course_year(self):
        domain = {'student_id': []}
        if self.course_id and self.year_id:
            domain['student_id'] = [
                ('student_class_name', '=', self.course_id.id),
                ('student_class', '=', self.year_id.id)
            ]
            _logger.info("Filtered students for course=%s, year=%s",
                         self.course_id.name, self.year_id.name)
        elif self.course_id:
            domain['student_id'] = [('student_class_name', '=', self.course_id.id)]
            _logger.info("Filtered students for course=%s", self.course_id.name)
        elif self.year_id:
            domain['student_id'] = [('student_class', '=', self.year_id.id)]
            _logger.info("Filtered students for year=%s", self.year_id.name)
        else:
            _logger.info("No course/year selected, student list cleared")
        return {'domain': domain}

    # @api.onchange('student_id')
    # def _onchange_student_id(self):
    #     """Update course and year based on student"""
    #     if self.student_id:
    #         self.course_id = self.student_id.student_class_name.id
    #         self.year_id = self.student_id.student_class.id
    #         if self.student_id.academic_id:
    #             self.amount = self.student_id.academic_id.current_balance


        """ 
        # Update academic record with payment
        for rec in records:
            if rec.academic_id and rec.amount > 0:
                try:
                    # Call the add_fee_payment method instead of direct write
                    rec.academic_id.add_fee_payment(rec.amount)

                    # Update student master record
                    rec.student_id.write({
                        'total_fees_receipted': rec.student_id.total_fees_receipted + rec.amount
                    })

                    _logger.info(
                        f"Successfully processed payment of {rec.amount} for student {rec.student_id.student_name}")

                except UserError as e:
                    # Log the error and raise it
                    _logger.error(f"Error processing payment for student {rec.student_id.student_name}: {e}")
                    raise UserError(f"Cannot create receipt: {e}")
                except Exception as e:
                    _logger.error(f"Unexpected error processing payment: {e}")
                    raise UserError(f"Unexpected error occurred: {e}")

    """
        # # Restrict editing if locked
        # def write(self, vals):
        #     if any(rec.is_locked for rec in self):
        #         raise UserError(_("You cannot edit a locked receipt."))
        #     return super().write(vals)






class FeeUpdateWizard(models.TransientModel):
    _name = 'fee.update.wizard'
    _description = 'Fee Update Wizard'

    confirm = fields.Boolean(string="Confirm Fee Update?")
    can_execute = fields.Boolean(string="Can Execute", compute='_compute_can_execute', store=False)

    def action_generate_invoices(self):
        """ Generate quarterly invoices for all students """
        if not self.confirm:
            return {'type': 'ir.actions.act_window_close'}

        students = self.env['student.master'].search([])
        invoice_count = 0

        for student in students:
            course = student.student_class_name
            if course and course.quarter_fee > 0:
                # Always use course fee as description
                description = f"Quarterly Fee - {course.name}"

                invoice_vals = {
                    'student_id': student.id,
                    'course_id': course.id,
                    'year_id': student.student_class.id if student.student_class else False,
                    'invoice_date': fields.Date.today(),
                    'description': description,
                    'amount': course.quarter_fee,
                    'state': 'confirmed',
                    'company_id': self.env.company.id,
                }
                self.env['student.fee.invoice'].create(invoice_vals)
                invoice_count += 1

                _logger.info(
                    "Created invoice %.2f for student %s (Course: %s)",
                    course.quarter_fee, student.student_name, course.name
                )

        # Save execution date for quarterly restriction
        self.env['ir.config_parameter'].sudo().set_param(
            'fee_update.last_execution', fields.Datetime.now()
        )

        _logger.info("Quarterly invoices generated: %s", invoice_count)
        return {'type': 'ir.actions.act_window_close'}

    # @api.depends()
    # def _compute_can_execute(self):
    #     """ Allow execution only if 90+ days passed since last run """
    #     last_execution = self.env['ir.config_parameter'].sudo().get_param('fee_update.last_execution')
    #     if last_execution:
    #         last_date = fields.Datetime.from_string(last_execution)
    #         time_diff = (fields.Datetime.now() - last_date).days
    #         self.can_execute = time_diff >= 90
    #     else:
    #         self.can_execute = True
    @api.depends()
    def _compute_can_execute(self):
        """ Allow execution only if 5+ minutes passed since last run (for testing) """
        last_execution = self.env['ir.config_parameter'].sudo().get_param('fee_update.last_execution')
        if last_execution:
            last_date = fields.Datetime.from_string(last_execution)
            time_diff = (fields.Datetime.now() - last_date).total_seconds() / 60  # in minutes
            self.can_execute = time_diff >= 5  # 5 minutes for testing
        else:
            self.can_execute = True
