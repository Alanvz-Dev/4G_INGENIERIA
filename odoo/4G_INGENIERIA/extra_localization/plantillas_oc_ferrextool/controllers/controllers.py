# -*- coding: utf-8 -*-
from odoo import http

# class PlantillasFacturasFerrextool(http.Controller):
#     @http.route('/plantillas_facturas_ferrextool/plantillas_facturas_ferrextool/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plantillas_facturas_ferrextool/plantillas_facturas_ferrextool/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('plantillas_facturas_ferrextool.listing', {
#             'root': '/plantillas_facturas_ferrextool/plantillas_facturas_ferrextool',
#             'objects': http.request.env['plantillas_facturas_ferrextool.plantillas_facturas_ferrextool'].search([]),
#         })

#     @http.route('/plantillas_facturas_ferrextool/plantillas_facturas_ferrextool/objects/<model("plantillas_facturas_ferrextool.plantillas_facturas_ferrextool"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plantillas_facturas_ferrextool.object', {
#             'object': obj
#         })