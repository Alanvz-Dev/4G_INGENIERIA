# -*- coding: utf-8 -*-
from odoo import http

# class ReportesPdf(http.Controller):
#     @http.route('/slow_movement_xlsx/slow_movement_xlsx/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/slow_movement_xlsx/slow_movement_xlsx/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('slow_movement_xlsx.listing', {
#             'root': '/slow_movement_xlsx/slow_movement_xlsx',
#             'objects': http.request.env['slow_movement_xlsx.slow_movement_xlsx'].search([]),
#         })

#     @http.route('/slow_movement_xlsx/slow_movement_xlsx/objects/<model("slow_movement_xlsx.slow_movement_xlsx"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('slow_movement_xlsx.object', {
#             'object': obj
#         })