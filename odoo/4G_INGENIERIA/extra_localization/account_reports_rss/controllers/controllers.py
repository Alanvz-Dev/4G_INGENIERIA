# -*- coding: utf-8 -*-
from odoo import http

# class AccountReports4G(http.Controller):
#     @http.route('/account_reports_rss/account_reports_rss/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_reports_rss/account_reports_rss/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_reports_rss.listing', {
#             'root': '/account_reports_rss/account_reports_rss',
#             'objects': http.request.env['account_reports_rss.account_reports_rss'].search([]),
#         })

#     @http.route('/account_reports_rss/account_reports_rss/objects/<model("account_reports_rss.account_reports_rss"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_reports_rss.object', {
#             'object': obj
#         })