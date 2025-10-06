# -*- coding: utf-8 -*-
import re
from datetime import date

import dateutil
import self

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class StudentMaster(models.Model):
    _name = 'student.master'
    _description = 'Student Master'
    _rec_name = 'student_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Admission Number', readonly=True, default='New')
    admission_date = fields.Date('Admission Date', default=fields.Date.today())
    student_name = fields.Char(string='Student Name ', required=True, tracking=True)
    student_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender ')
    reg_no = fields.Char('University Reg No',tracking=True)
    is_sponsor = fields.Boolean('Is Sponsored ?',default=False,tracking=True)
    sponsor_note = fields.Text('Sponsor Details',tracking=True)
    is_concession = fields.Boolean('Is Concession ?',default=False,tracking=True)
    concession_note = fields.Text('Concession Details',tracking=True)
    dob = fields.Date(string='D O B ')
    age = fields.Integer(string='Age ', compute='_compute_age', readonly=True, store=False)
    teacher_id = fields.Many2one('teacher.master', string='Teacher ')
    student_roll_number = fields.Integer(string='Roll Number ')
    student_guardian = fields.Char(string='Daughter/Son Of ')
    student_add = fields.Text('Address ')
    pincode = fields.Char('Pin Code ')
    student_add1 = fields.Char(string='House Name ', )
    student_add2 = fields.Char(string='Location ')
    student_add3 = fields.Char(string='City ')
    student_contact1 = fields.Char(string='Student Mobile ', size=10)
    student_contact2 = fields.Char(string=' Guardian Mobile ', size=10)
    student_img = fields.Image(string='Photo ', max_width=128, max_height=128)
    student_trans = fields.Selection([('school_bus', 'School Bus'), ('auto', 'Auto'), ('self', 'Self')],
                                     string='Transportation ')
    transport_mode = fields.Selection([('one_way', 'One Way'), ('two_way', 'Two Way')], string='Transportation Mode ')
    is_locked = fields.Boolean(string='Locked', default=False)
    aadhaar_card = fields.Char(string='Aadhaar Card No ')
    has_aadhaar = fields.Boolean(compute='_compute_has_aadhaar', store=True)
    active = fields.Boolean(string='Active', default=True)
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    course_id = fields.Many2one('student.class.name', string="Course", required=True,tracking=True)
    year_id = fields.Many2one(
        'course.year.line',string="Year",domain="[('course_id', '=', course_id)]", required=True,tracking=True)
    course_year_batch_key = fields.Char(compute="_compute_course_year_batch_key",store=True, index=True)
    total_fees_accumulated = fields.Float(string='Total Fees Accumulated', default=0.0, readonly=True)
    total_fees_receipted = fields.Float(string='Total Receipted Amount', default=0.0, readonly=True)
    current_balance = fields.Float(
        string="Current Balance :",
        compute="_compute_current_balance",
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)
    #last_fee_addition = fields.Datetime(string='Last Fee Addition', readonly=True)
    exam_ids = fields.One2many('exam.result', 'student_id', string='Exam Details')
    transport_ids = fields.One2many('student.transportation', 'student_id', string="Transport Details")
    monthly_fee_ids = fields.One2many('transport.monthly.fee', 'transport_id', string='Monthly Fees')
    fee_invoice_ids = fields.One2many('student.fee.invoice', 'student_id', string="Invoices")
    fee_receipt_ids = fields.One2many('student.fee.receipt', 'student_id', string="Receipts")
    document_collection_ids = fields.One2many('student.documents.collection', 'student_id',
        string='Document Collections')
    pending_document_ids = fields.One2many('student.documents.line',compute='_compute_pending_documents',
        string='Pending Documents',store=False)
    receipt_type = fields.Selection([
        ('charge', 'Charge'),
        ('payment', 'Payment')
    ], default='payment', string="Type", tracking=True)

    key = fields.Char(compute="_compute_key", store=True, index=True)

    @api.depends('course_id', 'year_id', )
    def _compute_course_year_batch_key(self):
        for rec in self:
            rec.course_year_batch_key = f"{rec.course_id.id}-{rec.year_id.id}"

    @api.depends('course_id', 'year_id')
    def _compute_key(self):
        for rec in self:
            rec.key = f"{rec.course_id.id}-{rec.year_id.id}" if rec.course_id and rec.year_id else False

    _sql_constraints = [
        ('roll_number_unique', 'UNIQUE(student_roll_number, year_id,course_id)',
         'Roll number must be unique.')
    ]

    @api.depends('dob')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.dob:
                dob = fields.Date.from_string(record.dob)
                record.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.age = 0

    def action_save(self):
        self.write({'is_locked': True})
        for rec in self:
            rec.state = 'confirmed'

            # Create Admission Fee Invoice (with duplicate check)
            existing_admission = self.env['student.fee.invoice'].search([
                ('student_id', '=', rec.id),
                ('invoice_type', '=', 'admission')
            ], limit=1)

            if not existing_admission and rec.course_id and rec.course_id.admission_fee > 0:
                self.env['student.fee.invoice'].create({
                    'student_id': rec.id,
                    'course_id': rec.course_id.id,
                    'year_id': rec.year_id.id if rec.year_id else False,
                    'amount': rec.course_id.admission_fee,
                    'description': 'Admission Fee',
                    'invoice_type': 'admission',
                })

            # Create Term One Fee Invoice (with duplicate check)
            existing_term_one = self.env['student.fee.invoice'].search([
                ('student_id', '=', rec.id),
                ('invoice_type', '=', 'term_one')
            ], limit=1)

            if not existing_term_one and rec.course_id and rec.course_id.term_one_fee > 0:
                self.env['student.fee.invoice'].create({
                    'student_id': rec.id,
                    'course_id': rec.course_id.id,
                    'year_id': rec.year_id.id if rec.year_id else False,
                    'amount': rec.course_id.term_one_fee,
                    'description': 'Term One Fee',
                    'invoice_type': 'term_one',
                })

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}


    def action_go_back(self):
       action = self.env["ir.actions.actions"]._for_xml_id("school_master_pro.action_student_master")
       action["clear_breadcrumbs"] = True
       action["target"] = "main"
       return action

        # This will navigate back to the action that opens the Kanban/Tree view
       # action = self.env.ref('school_master_pro.action_student_master').read()[0]
        #action['target'] = 'main'
        #return action

    @api.depends('aadhaar_card')
    def _compute_has_aadhaar(self):
        for record in self:
            record.has_aadhaar = bool(record.aadhaar_card and record.aadhaar_card.strip())

    @api.constrains('aadhaar_card')
    def _check_aadhaar_number(self):
        for record in self:
            if record.aadhaar_card and record.aadhaar_card.strip():
                # Remove spaces or hyphens if any
                aadhaar_clean = re.sub(r'[\s-]', '', record.aadhaar_card)
                if not aadhaar_clean.isdigit() or len(aadhaar_clean) != 12:
                    raise ValidationError("Aadhaar number must be 12 digits (numbers only)")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('student.sequence.master') or 'New'
        records = super().create(vals_list)
        return records

    def action_pay_now(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Payment',
            'res_model': 'student.fee.receipt',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_student_id': self.id,
                'default_amount': self.current_balance,
                'default_course_id': self.course_id.id if self.course_id else False,
                'default_year_id': self.year_id.id if self.year_id else False,
                'reload_parent_form': True,
            },
        }

    @api.depends('fee_invoice_ids.original_amount', 'fee_invoice_ids.state',
                 'fee_receipt_ids.amount', 'fee_receipt_ids.state')
    def _compute_current_balance(self):
        for rec in self:
            # always take original invoice totals
            charges = sum(inv.original_amount for inv in rec.fee_invoice_ids if inv.state == 'confirmed')
            # payments + concessions reduce balance
            reductions = sum(rc.amount for rc in rec.fee_receipt_ids if rc.state == 'confirmed')
            rec.current_balance = charges - reductions

    @api.depends('document_collection_ids.document_line_ids.returned_date')
    def _compute_pending_documents(self):
        for student in self:
            student.pending_document_ids = student.document_collection_ids.mapped('document_line_ids').filtered(
                lambda line: not line.returned_date
            )

    def action_open_concession_wizard(self):
        return {
            "name": "Apply Concession",
            "type": "ir.actions.act_window",
            "res_model": "student.concession.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_student_id": self.id},
        }

    @api.constrains("course_id", "year_id")
    def _check_course_year_match(self):
        for rec in self:
            if rec.course_id and rec.year_id and rec.year_id.course_id != rec.course_id:
                raise ValidationError(
                    f"Selected Year '{rec.year_id.display_name}' does not belong to Course '{rec.course_id.display_name}'.")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.user.teacher_id:
            teacher = self.env.user.teacher_id
            res['teacher_id'] = teacher.id
            if teacher.course_year_batch_ids:
                res['course_id'] = teacher.course_year_batch_ids[0].course_id.id
                res['year_id'] = teacher.course_year_batch_ids[0].year_id.id
        return res

    def action_auto_promote_next_year(self):
        # Promote students to next academic year (on/after May 1),
        # carry forward pending balance, and create new Term One fee.

        today = date.today()
        promoted_count = 0

        if today.month < 5:
            _logger.info("⏳ Promotion skipped: current date before May 1 (%s)", today)
            return 0

        for student in self.search([('state', '=', 'confirmed')]):
            course = student.course_id
            current_year = student.year_id
            if not course or not current_year:
                continue

            # Get course years (in correct order)
            all_years = self.env['course.year.line'].search([
                ('course_id', '=', course.id)
            ], order='id asc')

            if current_year.id not in all_years.ids:
                continue

            current_index = all_years.ids.index(current_year.id)
            if current_index == len(all_years) - 1:
                continue  # Already last year

            next_year = all_years[current_index + 1]
            fee_model = self.env['student.fee.invoice']

            # 🔹 1. Calculate unpaid balance
            unpaid_invoices = student.fee_invoice_ids.filtered(
                lambda inv: inv.state == 'confirmed' and inv.amount > 0
            )
            total_paid = sum(r.amount for r in student.fee_receipt_ids if r.state == 'confirmed')
            total_charged = sum(inv.original_amount for inv in unpaid_invoices)
            balance = total_charged - total_paid

            # 🔹 2. Promote student
            student.write({'year_id': next_year.id})

            # 🔹 3. Carry forward balance, if any
            if balance > 0:
                fee_model.create({
                    'student_id': student.id,
                    'course_id': course.id,
                    'year_id': next_year.id,
                    'invoice_date': fields.Date.today(),
                    'description': f"Carry Forward Balance from {current_year.name}",
                    'amount': balance,
                    'invoice_type': 'carry_forward',
                    'state': 'confirmed',
                    'is_locked': True,
                })

            # 🔹 4. Create Term 1 for new year (no admission fee)
            if course.term_one_fee > 0:
                fee_model.create({
                    'student_id': student.id,
                    'course_id': course.id,
                    'year_id': next_year.id,
                    'invoice_date': fields.Date.today(),
                    'description': f"{next_year.name} - Term One Fee",
                    'amount': course.term_one_fee,
                    'invoice_type': 'term_one',
                    'state': 'confirmed',
                    'is_locked': True,
                })

            promoted_count += 1

        _logger.info("🎓 Auto-promoted %s students (carry forward balances handled)", promoted_count)
        return promoted_count




    """ 
    @api.constrains('student_class_name')
    def _check_course_capacity(self):
        for rec in self:
            if rec.student_class_name:
                enrolled = self.env['student.master'].search_count([
                    ('student_class_name', '=', rec.student_class_name.id),
                    ('id', '!=', rec.id),  # exclude current record
                    ('active', '=', True)
                ])
                if enrolled >= rec.student_class_name.max_count:
                    raise ValidationError(
                        f"Course '{rec.student_class_name.name}' has reached its maximum capacity "
                        f"({rec.student_class_name.max_count} students)."
                    )

    @api.constrains('student_class_name', 'student_class')
    def _check_course_capacity(self):
        for rec in self:
            if rec.student_class_name and rec.student_class:
                enrolled = self.env['student.master'].search_count([
                    ('student_class_name', '=', rec.student_class_name.id),
                    ('student_class', '=', rec.student_class.id),
                    ('id', '!=', rec.id),
                    ('active', '=', True)
                ])
                if enrolled >= rec.student_class_name.max_count:
                    raise ValidationError(
                        f"Course '{rec.student_class_name.name}' - Year '{rec.student_class.name}' "
                        f"has reached its maximum capacity ({rec.student_class_name.max_count} students)."
                    )
                    
      def create_new_student(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "student.master",
            "view_mode": "form",
            "target": "current",
            "context": {"default_state": "draft"},
        }
    """