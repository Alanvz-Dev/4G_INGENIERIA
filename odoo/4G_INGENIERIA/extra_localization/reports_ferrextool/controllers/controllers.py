# -*- coding: utf-8 -*-
from odoo import http

# class ReportsFerrextool(http.Controller):
#     @http.route('/reports_ferrextool/reports_ferrextool/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reports_ferrextool/reports_ferrextool/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reports_ferrextool.listing', {
#             'root': '/reports_ferrextool/reports_ferrextool',
#             'objects': http.request.env['reports_ferrextool_exceso_de_inventario'].search([]),
#         })

#     @http.route('/reports_ferrextool/reports_ferrextool/objects/<model("reports_ferrextool_exceso_de_inventario"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reports_ferrextool.object', {
#             'object': obj
#         })