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

    @http.route('/create_employee', type='http', auth='user', methods=['POST'], website=True)
    def create_employee(self, **post):
        # Get form data
        name = post.get('name')
        manager_id = post.get('manager_id')

        # Convert manager_id to int if exists
        manager_id = int(manager_id) if manager_id else False

        # Create new employee
        request.env['hr.employee'].sudo().create({
            'name': name,
            'parent_id': manager_id
        })

        # Redirect back to employee list
        return request.redirect('/my/employees')
    
    @http.route(['/my/employee_expense'], type='http', auth="user", website=True)
    def account_home(self, **kw):
        """return home to click home in dashboard page"""
        values = self._prepare_portal_layout_values()
        return request.render("skit_customer_portal.account_dashbord", values)

