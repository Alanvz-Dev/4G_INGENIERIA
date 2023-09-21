# -*- coding: utf-8 -*-
from odoo import http

# class HrPayroll4g(http.Controller):
#     @http.route('/hr_payroll_4g/hr_payroll_4g/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_payroll_4g/hr_payroll_4g/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_payroll_4g.listing', {
#             'root': '/hr_payroll_4g/hr_payroll_4g',
#             'objects': http.request.env['hr_payroll_4g.hr_payroll_4g'].search([]),
#         })

#     @http.route('/hr_payroll_4g/hr_payroll_4g/objects/<model("hr_payroll_4g.hr_payroll_4g"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_payroll_4g.object', {
#             'object': obj
#         })