# -*- coding: utf-8 -*-
from odoo import http

# class PlantillasFacturas4g(http.Controller):
#     @http.route('/plantillas_facturas_4g/plantillas_facturas_4g/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plantillas_facturas_4g/plantillas_facturas_4g/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('plantillas_facturas_4g.listing', {
#             'root': '/plantillas_facturas_4g/plantillas_facturas_4g',
#             'objects': http.request.env['plantillas_facturas_4g.plantillas_facturas_4g'].search([]),
#         })

#     @http.route('/plantillas_facturas_4g/plantillas_facturas_4g/objects/<model("plantillas_facturas_4g.plantillas_facturas_4g"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plantillas_facturas_4g.object', {
#             'object': obj
#         })