from odoo import models


class ReceiptWarningWizard(models.TransientModel):
    _name = 'receipt.warning.wizard'
    _description = 'Student Receipt Warning Wizard'

    def action_proceed_to_receipts(self):
        """Close wizard and replace entire history with receipts view"""
        return {
            'type': 'ir.actions.client',
            'tag': 'do-action-replace-history',
            'params': {
                'action': {
                    'type': 'ir.actions.act_window',
                    'name': 'Student Receipts',
                    'res_model': 'student.fee.receipt',
                    'view_mode': 'list,form',
                    'target': 'current',
                    'views': [[False, 'list'], [False, 'form']],
                    'context': {},
                }
            }
        }