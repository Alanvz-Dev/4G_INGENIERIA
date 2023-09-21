# -*- coding: utf-8 -*-
from odoo import http

# class AccountReports4G(http.Controller):
#     @http.route('/account_reports_4g/account_reports_4g/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_reports_4g/account_reports_4g/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_reports_4g.listing', {
#             'root': '/account_reports_4g/account_reports_4g',
#             'objects': http.request.env['account_reports_4g.account_reports_4g'].search([]),
#         })

#     @http.route('/account_reports_4g/account_reports_4g/objects/<model("account_reports_4g.account_reports_4g"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_reports_4g.object', {
#             'object': obj
#         })