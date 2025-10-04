# -*- coding: utf-8 -*-
# imports of odoo
from odoo import api, fields, models, _


class ApprovalRulesApprover(models.Model):
    _name = 'approval.rules.approver'
    _description = 'Approval Rules Approver'

    approver_id = fields.Many2one('approval.rules', string='Base Approver')
    user_id=fields.Many2one('res.users',string='Approver',required=True)
    is_approver = fields.Boolean(default=False, string='Is Required')