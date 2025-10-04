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
    
    @http.route('/my/employee_expense', type='http', auth='user', website=True)
    def view_employee_expense_form(self, **kwargs):
        expense = request.env['hr.expense'].sudo().search([("employee_id.user_id", "=", request.env.user.id)])
        expense_amt = expense.get_expense_dashboard()
        to_submit_amount = expense_amt['to_submit']['amount']
        submitted_amount = expense_amt['submitted']['amount']
        approved_amount = expense_amt['approved']['amount']
        return request.render('approval_expense.employee_expense', {
            'expenses': expense,
            'to_submit_amount':to_submit_amount,
            'submitted_amount':submitted_amount,
            'approved_amount':approved_amount
            
        })
        
    @http.route('/my_expense/new', type='http', auth='user', website=True)
    def new_employee_expense_form(self, **kwargs):
        expense = request.env['hr.expense'].sudo().search([("employee_id.user_id", "=", request.env.user.id)])
        return request.render('approval_expense.employee_expense_new', {
            'expenses': expense,
        })
    
