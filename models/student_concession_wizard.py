# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StudentConcessionWizard(models.TransientModel):
    _name = "student.concession.wizard"
    _description = "Student Concession Wizard"

    student_id = fields.Many2one("student.master", string="Student", required=True, readonly=True)
    admission_discount = fields.Float("Admission Fee Discount (Amount)")
    course_discount = fields.Float("Course Fee Discount (Amount)")
    term_one_discount = fields.Float("Term-1 Fee Discount (Amount)")
    term_two_discount = fields.Float("Term-2 Fee Discount (Amount)")
    term_three_discount = fields.Float("Term-3 Fee Discount (Amount)")
    note = fields.Text("Concession Note")

    def _apply_discount_to_invoice(self, invoice_type, discount_amount):
        """Apply concession only as a receipt, without changing invoice amounts."""
        if not discount_amount or discount_amount <= 0:
            return False

        invoice = self.env['student.fee.invoice'].search([
            ('student_id', '=', self.student_id.id),
            ('state', '=', 'confirmed'),
            ('invoice_type', '=', invoice_type),
        ], order='invoice_date desc, id desc', limit=1)

        if not invoice:
            return False

        # ✅ safer label lookup for nice receipt reference
        label = dict(invoice._fields['invoice_type'].selection).get(invoice.invoice_type, invoice.invoice_type)

        # create concession receipt (don’t touch invoice)
        self.env['student.fee.receipt'].create({
            'student_id': self.student_id.id,
            'course_id': invoice.course_id.id,
            'year_id': invoice.year_id.id,
            'amount': discount_amount,
            'payment_date': fields.Datetime.now(),
            'payment_method': 'cash',  # you can add "concession" if needed
            'reference': f"Concession on {label}",
            'receipt_type': 'concession',  # 👈 important: separate from payments
            'state': 'confirmed',
            'is_locked': True,
        })
        return True

    def action_apply_concession(self):
        self.ensure_one()
        applied_adm = self._apply_discount_to_invoice('admission', self.admission_discount or 0.0)
        applied_t1 = self._apply_discount_to_invoice('term_one', self.term_one_discount or 0.0)
        applied_t2 = self._apply_discount_to_invoice('term_two', self.term_two_discount or 0.0)
        applied_t3 = self._apply_discount_to_invoice('term_three', self.term_three_discount or 0.0)

        if self.note:
            self.student_id.concession_note = self.note

        if not any([applied_adm, applied_t1, applied_t2, applied_t3]):
            raise UserError(_("No confirmed invoice found for this student (admission/term fees)."))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Concession Applied'),
                'message': _('Discounts applied and logged as receipts.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}  # ✅ auto close wizard
            }
        }

