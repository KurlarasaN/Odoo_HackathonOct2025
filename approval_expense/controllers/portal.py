# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict

from odoo import fields, http, _
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.account.controllers.download_docs import _get_headers, _build_zip_from_data
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class PortalExpense(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'approval_expense_count' in counters:
            values['approval_expense_count'] = request.env['hr.expense'] \
                .sudo().search_count(
                [('employee_id.parent_id', '=', request.env.user.employee_id.id),
                 ('state','not in', ['draft','reported'])])

        if 'employee_expense_count' in counters:
            values['employee_expense_count'] = request.env['hr.expense'] \
                .sudo().search_count(
                [('employee_id', '=', request.env.user.employee_id.id)])
        if 'user_count' in counters:
            values['user_count'] = request.env['res.users'] \
                .sudo().search_count(
                [])
        return values

    @http.route(['/my/approval_expenses', '/my/approval_expenses/page/<int:page>'], type='http', auth="public", website=True)
    def portal_approval_expenses(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_my_expenses_approval_values(page, date_begin, date_end, sortby, filterby)

        # pager
        pager = portal_pager(**values['pager'])

        # content according to pager and archive selected
        expenses = values['expenses'](pager['offset'])
        request.session['my_expenses_history'] = [e['expense'].id for e in expenses][:100]

        values.update({
            'expenses': expenses,
            'pager': pager,
        })
        return request.render("approval_expense.portal_my_approval_expenses", values)
    
    def _get_expense_domain(self, m_type=None):
        return [('employee_id.parent_id', '=', request.env.user.employee_id.id),
                ('state','not in', ['draft','reported'])]
    
    def _get_expense_searchbar_sortings(self):
        return {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'total_amount': {'label': _('Total Amount'), 'order': 'total_amount desc'},
            'employee_id': {'label': _('Request Owner'), 'order': 'employee_id desc'},
            'state': {'label': _('Request Status'), 'order': 'state'},
        }
    
    def _get_expenses_searchbar_filters(self):
        return {
            'all': {'label': _('All'), 'domain': []},
            'approved': {'label': _('Approved'), 'domain': [('state', '=', 'approved')]},
            'rejected': {'label': _('Rejected'), 'domain': [('state', '=', 'refused')]},
        }
    
    def _prepare_my_expenses_approval_values(self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/approval_expenses"):
        values = self._prepare_portal_layout_values()
        HRExpenses = request.env['hr.expense']

        domain = expression.AND([
            domain or [],
            self._get_expense_domain(),
        ])

        searchbar_sortings = self._get_expense_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_expenses_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        values.update({
            'date': date_begin,
            # content according to pager and archive selected
            # lambda function to get the invoices recordset when the pager will be defined in the main method of a route
            'expenses': lambda pager_offset: (
                [
                    expense._get_expense_portal_extra_values()
                    for expense in HRExpenses.search(
                        domain, order=order, limit=self._items_per_page, offset=pager_offset
                    )
                ]
                if HRExpenses.has_access('read') else
                HRExpenses
            ),
            'page_name': 'expense',
            'pager': {  # vals to define the pager.
                "url": url,
                "url_args": {'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
                "total": HRExpenses.search_count(domain) if HRExpenses.has_access('read') else 0,
                "page": page,
                "step": self._items_per_page,
            },
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return values
    
    @http.route(['/expense/approved/<int:expense_id>'], type='http', auth="user", website=True)
    def approved_expense(self, expense_id):
        expense_sheet = request.env['hr.expense.sheet'].sudo().search([('expense_line_ids','in', [expense_id])])
        print(expense_sheet)
        if expense_sheet:
            expense_sheet.action_approve_expense_sheets()
        return request.redirect('/my/approval_expenses')
    
    @http.route(['/expense/reject/<int:expense_id>'], type='http', auth="user", website=True)
    def refused_expense(self, expense_id):
        expense_sheet = request.env['hr.expense.sheet'].sudo().search([('expense_line_ids','in', [expense_id])])
        print(expense_sheet)
        if expense_sheet:
            expense_sheet.action_refuse_expense_sheets()
        return request.redirect('/my/approval_expenses')
        
        