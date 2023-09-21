# -*- coding: utf-8 -*-
from odoo import http

# class Hr4gPayrollExt(http.Controller):
#     @http.route('/hr_4g_payroll_ext/hr_4g_payroll_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_4g_payroll_ext/hr_4g_payroll_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_4g_payroll_ext.listing', {
#             'root': '/hr_4g_payroll_ext/hr_4g_payroll_ext',
#             'objects': http.request.env['hr_4g_payroll_ext.hr_4g_payroll_ext'].search([]),
#         })

#     @http.route('/hr_4g_payroll_ext/hr_4g_payroll_ext/objects/<model("hr_4g_payroll_ext.hr_4g_payroll_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_4g_payroll_ext.object', {
#             'object': obj
#         })