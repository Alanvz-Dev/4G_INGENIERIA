# -*- coding: utf-8 -*-
from odoo import http

# class AxtraxngAttendance(http.Controller):
#     @http.route('/axtraxng_attendance/axtraxng_attendance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/axtraxng_attendance/axtraxng_attendance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('axtraxng_attendance.listing', {
#             'root': '/axtraxng_attendance/axtraxng_attendance',
#             'objects': http.request.env['axtraxng_attendance.axtraxng_attendance'].search([]),
#         })

#     @http.route('/axtraxng_attendance/axtraxng_attendance/objects/<model("axtraxng_attendance.axtraxng_attendance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('axtraxng_attendance.object', {
#             'object': obj
#         })