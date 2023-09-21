# -*- coding: utf-8 -*-
from odoo import http

# class AccountReportsFERREXTOOL(http.Controller):
#     @http.route('/account_reports_ferrextool/account_reports_ferrextool/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_reports_ferrextool/account_reports_ferrextool/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_reports_ferrextool.listing', {
#             'root': '/account_reports_ferrextool/account_reports_ferrextool',
#             'objects': http.request.env['account_reports_ferrextool.account_reports_ferrextool'].search([]),
#         })

#     @http.route('/account_reports_ferrextool/account_reports_ferrextool/objects/<model("account_reports_ferrextool.account_reports_ferrextool"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_reports_ferrextool.object', {
#             'object': obj
#         })