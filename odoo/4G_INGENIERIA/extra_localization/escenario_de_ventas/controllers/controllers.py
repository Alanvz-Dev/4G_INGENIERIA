# -*- coding: utf-8 -*-
from odoo import http

# class EscenarioDeVentas(http.Controller):
#     @http.route('/escenario_de_ventas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/escenario_de_ventas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('escenario_de_ventas.listing', {
#             'root': '/escenario_de_ventas',
#             'objects': http.request.env['escenario_de_ventas.escenario_de_ventas'].search([]),
#         })

#     @http.route('/escenario_de_ventas/objects/<model("escenario_de_ventas.escenario_de_ventas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('escenario_de_ventas.object', {
#             'object': obj
#         })