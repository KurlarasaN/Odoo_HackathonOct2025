# -*- coding: utf-8 -*-
# imports of odoo
from odoo import api, fields, models, _


class ApprovalRules(models.Model):
    _name = 'approval.rules'
    _description = 'Approval Rules'
    _rec_name = 'name'

    name = fields.Char(string='Approval Rule', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    approver_ids= fields.One2many('approval.rules.approver', 'approver_id')

    def action_travel_policy(self):
        """ Action Open Travel Meal Policy Form view"""
        record = self.env['approval.rules'].search([])
        return {
            'name': 'Approval Rules',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.rules',
            'view_mode': 'form',
            'view_id': self.env.ref('approval_expense.view_travel_meal_policy_form').id,
            'res_id': record.id,
            'target': 'current',
            'context':{'create': False}
        }
