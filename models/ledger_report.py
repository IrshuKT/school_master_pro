from odoo import models, fields, api
from datetime import datetime


class LedgerReport(models.TransientModel):
    _name = 'ledger.report'
    _description = 'Each Ledger Report'

    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    ledger_name = fields.Many2one('finance.head', string='Select Ledger')
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    def get_transaction_data(self):
        """Prepare transaction data for the report"""
        self.ensure_one()

        domain = []
        if self.ledger_name:
            domain.append(('head_id', '=', self.ledger_name.id))
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))

        transactions = self.env['finance.voucher'].search(domain, order='date asc')

        # Prepare data in a format that can be serialized
        transaction_data = []
        total_debit = 0
        total_credit = 0

        for transaction in transactions:
            debit = transaction.amount if transaction.voucher_type == 'receipt' else 0
            credit = transaction.amount if transaction.voucher_type == 'payment' else 0

            total_debit += debit
            total_credit += credit

            # Format date as DD-MM-YYYY or DD/MM/YYYY
            formatted_date = transaction.date.strftime('%d-%m-%Y') if transaction.date else ''

            transaction_data.append({
                'date': formatted_date,
                'name': transaction.name or '',
                'description': transaction.description or '',
                'partner_id': transaction.partner_id or '',
                'voucher_type': transaction.voucher_type or '',
                'debit': debit,
                'credit': credit,
            })

        return {
            'transactions': transaction_data,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'balance': total_debit - total_credit,
        }

    def get_formatted_date_from(self):
        """Return formatted date_from"""
        if self.date_from:
            return self.date_from.strftime('%d-%m-%Y')
        return ''

    def get_formatted_date_to(self):
        """Return formatted date_to"""
        if self.date_to:
            return self.date_to.strftime('%d-%m-%Y')
        return ''

    def get_current_date(self):
        """Return current date formatted"""
        return fields.Date.today().strftime('%d-%m-%Y')

    def action_get(self):
        """Generate the report"""
        if not self.ledger_name:
            raise models.ValidationError("Please select a ledger!")

        return self.env.ref('school_master_pro.ledger_report_action').report_action(self)

    def action_clear(self):
        self.write({
            'date_from': False,
            'date_to': False,
            'ledger_name': False,
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}