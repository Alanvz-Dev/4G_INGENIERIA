# -*- coding: utf-8 -*-
from odoo import http

# class EmployeeMods(http.Controller):
#     @http.route('/employee_mods/employee_mods/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_mods/employee_mods/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_mods.listing', {
#             'root': '/employee_mods/employee_mods',
#             'objects': http.request.env['employee_mods.employee_mods'].search([]),
#         })

#     @http.route('/employee_mods/employee_mods/objects/<model("employee_mods.employee_mods"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_mods.object', {
#             'object': obj
#         })