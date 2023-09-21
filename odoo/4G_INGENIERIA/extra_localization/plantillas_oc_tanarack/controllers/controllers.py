# -*- coding: utf-8 -*-
from odoo import http

# class PlantillasFacturasTanarack(http.Controller):
#     @http.route('/plantillas_facturas_tanarack/plantillas_facturas_tanarack/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plantillas_facturas_tanarack/plantillas_facturas_tanarack/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('plantillas_facturas_tanarack.listing', {
#             'root': '/plantillas_facturas_tanarack/plantillas_facturas_tanarack',
#             'objects': http.request.env['plantillas_facturas_tanarack.plantillas_facturas_tanarack'].search([]),
#         })

#     @http.route('/plantillas_facturas_tanarack/plantillas_facturas_tanarack/objects/<model("plantillas_facturas_tanarack.plantillas_facturas_tanarack"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plantillas_facturas_tanarack.object', {
#             'object': obj
#         })