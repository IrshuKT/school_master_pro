# -*- coding: utf-8 -*-
from odoo import models, fields, api
class StudentLedger(models.Model):
        _name = 'student.ledger'
        _description = 'Student Ledger'
        _auto = False   # No DB table, purely SQL view
        _rec_name = 'date'

        student_id = fields.Many2one('student.master', string="Student", readonly=True)
        date = fields.Date(string="Date", readonly=True)
        description = fields.Char(string="Description", readonly=True)
        debit = fields.Float(string="Debit (Invoice)", readonly=True)
        credit = fields.Float(string="Credit (Receipt)", readonly=True)
        balance = fields.Float(string="Running Balance", compute="_compute_balance", store=False)

        company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
        company_id = fields.Many2one(
            'res.company', string='Company', default=lambda self: self.env.company, readonly=True)


        def init(self):
            self._cr.execute("""
                CREATE OR REPLACE VIEW student_ledger AS (
                    SELECT
                        inv.id as id,
                        inv.student_id,
                        inv.invoice_date as date,
                        inv.description as description,
                        inv.amount as debit,
                        0.0 as credit,
                        inv.company_id as company_id
                    FROM student_fee_invoice inv
                    WHERE inv.state = 'confirmed'
    
                    UNION ALL
    
                    SELECT
                        -rec.id as id,   -- negative IDs to avoid conflict
                        rec.student_id,
                        rec.payment_date::date as date,
                        rec.reference as description,
                        0.0 as debit,
                        rec.amount as credit,
                        rec.company_id as company_id
                    FROM student_fee_receipt rec
                    WHERE rec.state = 'confirmed'
                )
            """)

        @api.depends('student_id')
        def _compute_balance(self):
            """ Compute running balance per student """
            for student in self.mapped('student_id'):
                records = self.search([('student_id', '=', student.id)], order='date,id')
                balance = 0.0
                for rec in records:
                    balance += rec.debit - rec.credit
                    rec.balance = balance




class StudentLedgerWizard(models.TransientModel):
        _name = "student.ledger.wizard"
        _description = "Student Ledger Wizard"
        _rec_name = 'student_id'

        student_id = fields.Many2one('student.master', string="Student Name", required=True)
        date_from = fields.Date(string="From Date")
        date_to = fields.Date(string="To Date")
        result_html = fields.Html(string="Ledger", sanitize=False, readonly=True)

        company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
        company_id = fields.Many2one(
            'res.company', string='Company', default=lambda self: self.env.company, readonly=True)

        def action_generate_ledger(self):
            domain = [('student_id', '=', self.student_id.id)]
            if self.date_to:
                domain.append(('date', '<=', self.date_to))

            records = self.env['student.ledger'].search(domain, order="date,id")

            # --- Opening Balance ---
            opening_domain = [('student_id', '=', self.student_id.id)]
            if self.date_from:
                opening_domain.append(('date', '<', self.date_from))
            opening_records = self.env['student.ledger'].search(opening_domain)
            opening_balance = sum(r.debit - r.credit for r in opening_records)

            balance = opening_balance
            rows = f"""
                <tr style="background-color:#f5f5f5;font-weight:bold;">
                    <td>{self.date_from.strftime("%d-%m-%Y") if self.date_from else ''}</td>
                    <td colspan="3">Opening Balance</td>
                    <td style="text-align:right;" colspan="2">{opening_balance:.2f}</td>
                </tr>
            """

            # --- Transactions ---
            for rec in records.filtered(lambda r: not self.date_from or r.date >= self.date_from):
                balance += rec.debit - rec.credit
                date_str = rec.date.strftime("%d-%m-%Y") if rec.date else ""
                rows += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{rec.student_id.student_name or ''}</td>
                        <td>{rec.description or ''}</td>
                        <td style="text-align:right;color:green;">{rec.debit:.2f}</td>
                        <td style="text-align:right;color:red;">{rec.credit:.2f}</td>
                        <td style="text-align:right;">{balance:.2f}</td>
                    </tr>
                """

            # --- Closing Balance ---
            rows += f"""
                <tr style="background-color:#e0f7fa;font-weight:bold;">
                    <td>{self.date_to.strftime("%d-%m-%Y") if self.date_to else ''}</td>
                    <td colspan="4">Closing Balance</td>
                    <td style="text-align:right;">{balance:.2f}</td>
                </tr>
            """

            if not records and not opening_records:
                rows = "<tr><td colspan='6' style='text-align:center;'>No records found</td></tr>"

            self.result_html = f"""
                <style>
                    table.student-ledger {{
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 14px;
                    }}
                    table.student-ledger th, table.student-ledger td {{
                        border: 1px solid #ddd;
                        padding: 6px;
                    }}
                    table.student-ledger th {{
                        background-color: #4CAF50;
                        color: white;
                        text-align: center;
                    }}
                    table.student-ledger tr:nth-child(even){{background-color:#f9f9f9;}}
                    table.student-ledger tr:hover{{background-color:#f1f1f1;}}
                </style>
    
                <table class="student-ledger">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Student Name</th>
                            <th>Description</th>
                            <th>Debit</th>
                            <th>Credit</th>
                            <th>Balance</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            """

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'student.ledger.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'current',
            }

        def print_pdf(self):
            return self.env.ref('school_master_pro.report_student_ledger_pdf').report_action(self)

