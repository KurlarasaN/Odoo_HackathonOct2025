from odoo import http
from odoo.http import request
import random
import string

class EmployeePortal(http.Controller):

    # User Details
    @http.route('/user/details/<int:user_id>', type='http', auth='user', website=True, csrf=True)
    def user_details(self, user_id, **kwargs):
        user = request.env['res.users'].sudo().browse(user_id)
        current_manager = user.employee_ids[0].parent_id.user_id.id
        if not user.exists():
            return request.redirect('/my/users')

        # HR Expense groups only
        expense_groups = user.groups_id.filtered(
            lambda g: g.category_id.xml_id == 'base.module_category_human_resources_expenses'
        )

        # All possible managers (all users except self)
        managers = request.env['res.users'].sudo().search([('id', '!=', user.id)])

        return request.render('approval_expense.user_details_template', {
            'user': user,
            'manager': current_manager,
            'expense_groups': expense_groups,
            'managers': managers,
        })

    # Save Manager Update
    @http.route('/update_manager', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def update_manager(self, **post):
        user_id = int(post.get('user_id'))
        manager_id = post.get('manager_id') and int(post.get('manager_id')) or False

        user = request.env['res.users'].sudo().browse(user_id)
        if user.exists():
            user.sudo().write({'parent_id': manager_id})

        return request.redirect(f'/user/details/{user_id}')

    @http.route('/reset_user_password', type='http', auth='user', methods=['POST'], website=True)
    def reset_user_password(self, **post):
        user_id = int(post.get('user_id')) if post.get('user_id') else False
        if not user_id:
            return request.redirect('/my/users')

        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return request.redirect('/my/users')

        # Generate a random password
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Update the user's password
        user.sudo().write({'password': new_password})

        # Send email with new credentials
        template = request.env.ref('approval_expense.email_template_reset_password', raise_if_not_found=False)
        if not template:
            template = request.env['mail.template'].sudo().create({
                'name': 'Reset User Password',
                'subject': 'Your Login Credentials Updated',
                'body_html': (
                    '<p>Hello ${object.name},</p>'
                    '<p>Your login: <b>${object.login}</b></p>'
                    '<p>Your new password: <b>${object.new_password}</b></p>'
                ),
                'model_id': request.env['ir.model']._get('res.users').id,
            })

        template.sudo().with_context(new_password=new_password).send_mail(user.id, force_send=True)

        return request.redirect('/my/users')

    @http.route('/my/users', type='http', auth='user', website=True)
    def portal_my_employees(self, **kwargs):
        users = request.env['res.users'].sudo().search([])
        return request.render('approval_expense.portal_my_users_template', {'users': users})

    @http.route('/create_user_form_template', type='http', auth='user', website=True)
    def create_user_form(self, **kwargs):
        hr_expense_category = request.env.ref('base.module_category_human_resources_expenses')
        expense_groups = request.env['res.groups'].sudo().search([('category_id', '=', hr_expense_category.id)])

        return request.render('approval_expense.create_user_form_template', {'roles': expense_groups})

    @http.route('/create_user', type='http', auth='user', methods=['POST'], website=True)
    def create_user(self, **post):
        name = post.get('name')
        email = post.get('email')
        role_id = int(post.get('role_id')) if post.get('role_id') else False

        if not name or not email:
            return request.redirect('/create_user_form')

        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Create user
        user_vals = {
            'name': name,
            'login': email,
            'email': email,
            'password': password,
        }

        if role_id:
            user_vals['groups_id'] = [(4, role_id)]

        user = request.env['res.users'].sudo().create(user_vals)

        # Send email with login credentials
        template = request.env.ref('approval_expense.email_template_reset_password', raise_if_not_found=False)
        if not template:
            template = request.env['mail.template'].sudo().create({
                'name': 'New User Credentials',
                'subject': 'Your login credentials',
                'body_html': (
                    '<p>Hello ${object.name},</p>'
                    '<p>Your login: <b>${object.login}</b></p>'
                    '<p>Your password: <b>${object.new_password}</b></p>'
                ),
                'model_id': request.env['ir.model']._get('res.users').id,
            })

        template.sudo().with_context(new_password=password).send_mail(user.id, force_send=True)

        return request.redirect('/my/users')
    
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
    
