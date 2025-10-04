import operator

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import logging
import werkzeug
from werkzeug.urls import url_encode

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.http import request
from markupsafe import Markup

_logger = logging.getLogger(__name__)


class AuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        print("ttstsdsdsdf")
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if not request.env['ir.http']._verify_request_recaptcha_token('signup'):
                    raise UserError(_("Suspicious activity detected by Google reCaptcha."))

                self.do_signup(qcontext)

                # Set user to public if they were not signed in by do_signup
                # (mfa enabled)
                if request.session.uid is None:
                    public_user = request.env.ref('base.public_user')
                    request.update_env(user=public_user)

                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search_count([("login", "=", qcontext.get("login"))], limit=1):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.warning("%s", e)
                    qcontext['error'] = _("Could not create a new account.") + Markup('<br/>') + str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        #country list
        countries = request.env['res.country'].sudo().search([])
        qcontext['countries'] = countries
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def _prepare_signup_values(self, qcontext):
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        if qcontext.get('country_id'):
            values['country_id'] = int(qcontext.get('country_id'))
        return values