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
    student_id = fields.Many2one(
        'student.master',string='Student Name',
        domain="[('student_class_name','=',course_id), ('course.year.line','=',year_id)]",
        required=True,tracking=True)

    course_id = fields.Many2one(
        'student.class.name',string="Course",required=True)
    year_id = fields.Many2one(
        'course.year.line',string="Year",domain="[('course_id', '=', course_id)]", required=True)
    amount = fields.Float(string='Amount', required=True,tracking=True)
    payment_date = fields.Datetime(string='Payment Date', default=fields.Datetime.now)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ],string='Payment Method', default='cash',tracking=True)

    invoice_type = fields.Selection([
        ('admission', 'Admission Fee'),
        ('term_one', 'Term One Fee'),
        ('term_two', 'Term Two Fee'),
        ('term_three', 'Term Three Fee'),
    ], string='Invoice Type', tracking=True)

    voucher_type = fields.Selection([
        ("receipt", "Receipt"),
        ("payment", "Payment"),
    ], string="Voucher Type", default='receipt', required=True, )

    direction = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], string="Direction", required=True, default='in')

    # voucher_type = fields.Selection([
    #     ("receipt", "Receipt"),
    #     ("payment", "Payment"),
    # ], string="Voucher Type", required=True, )

    reference = fields.Char(string='Payment Reference',tracking=True)
    collected_by = fields.Many2one(
        'res.users', string='Collected By', default=lambda self: self.env.user
    )
    is_locked = fields.Boolean(string='Locked', default=False)
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    head_id = fields.Many2one(
        "finance.head",
        string="Head / Account", required=True, help="E.g. Student Fees, Donation, Salary, Vendor Payment")

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

    def action_save(self):
        account_type_map = {
            'cash': 'cash',
            'bank': 'bank',
        }

        for rec in self:
            rec.write({'is_locked': True})
            account_type = account_type_map.get(rec.payment_method, 'cash')

            txn_vals = {
                "date": rec.payment_date,
                "account_type": account_type,
                "head_id": rec.head_id.id,
                "amount": rec.amount,
                "direction": "in" if rec.voucher_type == "receipt" else "out",
                "description": f"{rec.voucher_type.title()} - {rec.head_id.name} ({rec.student_id.name})",
                "ref_model": "student.fee.receipt",
                "ref_id": rec.id,
            }

            existing_txn = self.env['finance.transaction'].search([
                ('ref_model', '=', 'student.fee.receipt'),
                ('ref_id', '=', rec.id)
            ], limit=1)

            if existing_txn:
                existing_txn.write(txn_vals)
            else:
                self.env['finance.transaction'].create(txn_vals)

            rec.state = "confirmed"

        # Trigger UI refresh for cash/bank book
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    # Locking / Unlocking
    # def action_save(self):
    #     for rec in self:
    #         rec.write({'is_locked': True})
    #         self.env["finance.transaction"].create({
    #             "date": rec.payment_date,
    #             "account_type": rec.payment_method,
    #             "head_id": rec.head_id.id,  # 🔥 Add this line
    #             "amount": rec.amount,
    #             "direction": "in" if rec.voucher_type == "receipt" else "out",            })
    #         rec.state = "confirmed"

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
