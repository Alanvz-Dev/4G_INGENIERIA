# -*- coding: utf-8 -*-
from odoo import http

# class PayrollReceipts(http.Controller):
#     @http.route('/payroll_receipts/payroll_receipts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payroll_receipts/payroll_receipts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payroll_receipts.listing', {
#             'root': '/payroll_receipts/payroll_receipts',
#             'objects': http.request.env['payroll_receipts.payroll_receipts'].search([]),
#         })

#     @http.route('/payroll_receipts/payroll_receipts/objects/<model("payroll_receipts.payroll_receipts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payroll_receipts.object', {
#             'object': obj
#         })