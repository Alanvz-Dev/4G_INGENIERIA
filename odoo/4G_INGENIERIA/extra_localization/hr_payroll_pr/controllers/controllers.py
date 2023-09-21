# -*- coding: utf-8 -*-
from odoo import http

# class HrPayroll4g(http.Controller):
#     @http.route('/hr_payroll_pr/hr_payroll_pr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_payroll_pr/hr_payroll_pr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_payroll_pr.listing', {
#             'root': '/hr_payroll_pr/hr_payroll_pr',
#             'objects': http.request.env['hr_payroll_pr.hr_payroll_pr'].search([]),
#         })

#     @http.route('/hr_payroll_pr/hr_payroll_pr/objects/<model("hr_payroll_pr.hr_payroll_pr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_payroll_pr.object', {
#             'object': obj
#         })