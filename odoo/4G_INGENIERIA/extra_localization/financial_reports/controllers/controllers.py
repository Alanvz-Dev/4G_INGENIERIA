# -*- coding: utf-8 -*-
from odoo import http

# class FinancialReports(http.Controller):
#     @http.route('/financial_reports/financial_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financial_reports/financial_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financial_reports.listing', {
#             'root': '/financial_reports/financial_reports',
#             'objects': http.request.env['financial_reports.detail'].search([]),
#         })

#     @http.route('/financial_reports/financial_reports/objects/<model("financial_reports.detail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financial_reports.object', {
#             'object': obj
#         })