from odoo import http
from odoo.http import request

class EmployeePortal(http.Controller):

    @http.route('/my/employees', type='http', auth='user', website=True)
    def portal_my_employees(self, **kwargs):
        # Fetch all employees
        employees = request.env['hr.employee'].sudo().search([])
        return request.render('approval_expense.portal_my_employees_template', {
            'employees': employees,
        })

    @http.route('/create_employee_form', type='http', auth='user', website=True)
    def create_employee_form(self, **kwargs):
        employees = request.env['hr.employee'].sudo().search([])
        return request.render('approval_expense.create_employee_form_template', {
            'employees': employees,
        })

    @http.route('/create_employee', type='http', auth='user', methods=['POST'], website=True)
    def create_employee(self, **post):
        name = post.get('name')
        manager_id = int(post.get('manager_id')) if post.get('manager_id') else False
        request.env['hr.employee'].sudo().create({
            'name': name,
            'parent_id': manager_id
        })
        return request.redirect('/my/employees')
    
    @http.route(['/my/employee_expense'], type='http', auth="user", website=True)
    def account_home(self, **kw):
        """return home to click home in dashboard page"""
        values = self._prepare_portal_layout_values()
        return request.render("skit_customer_portal.account_dashbord", values)

