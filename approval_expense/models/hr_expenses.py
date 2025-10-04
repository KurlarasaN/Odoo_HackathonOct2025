# -*- coding: utf-8 -*-

from odoo import models


class HrExpenses(models.Model):
    _inherit = 'hr.expense'
    
    def _get_expense_portal_extra_values(self, custom_amount=None):
        self.ensure_one()
        return {
            'expense': self,
            'currency': self.currency_id,
        }