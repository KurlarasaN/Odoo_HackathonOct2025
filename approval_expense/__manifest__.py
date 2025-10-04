# -*- coding: utf-8 -*-
{
    'name': 'Expense Management',
    'version': '1.0',
    'summary': '',
    'author': 'Crewxdev',
    'license': "OPL-1",
    'website': '',
    'description': """ """,
    'depends': ['website','hr','hr_expense','portal'],
    'data': [
            'views/signup.xml',
			'views/portal_templates.xml',
            'views/portal_employee_views.xml',
            'views/portal_employee_template.xml',
            'views/create_employee_form_template.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
