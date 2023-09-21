# -*- coding: utf-8 -*-
from odoo import http

# class AccountReports4G(http.Controller):
#     @http.route('/account_reports_corporativo/account_reports_corporativo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_reports_corporativo/account_reports_corporativo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_reports_corporativo.listing', {
#             'root': '/account_reports_corporativo/account_reports_corporativo',
#             'objects': http.request.env['account_reports_corporativo.account_reports_corporativo'].search([]),
#         })

#     @http.route('/account_reports_corporativo/account_reports_corporativo/objects/<model("account_reports_corporativo.account_reports_corporativo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_reports_corporativo.object', {
#             'object': obj
#         })