# -*- coding: utf-8 -*-
from odoo import http

# class AprobacionProveedores(http.Controller):
#     @http.route('/aprobacion_proveedores/aprobacion_proveedores/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aprobacion_proveedores/aprobacion_proveedores/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aprobacion_proveedores.listing', {
#             'root': '/aprobacion_proveedores/aprobacion_proveedores',
#             'objects': http.request.env['aprobacion_proveedores.aprobacion_proveedores'].search([]),
#         })

#     @http.route('/aprobacion_proveedores/aprobacion_proveedores/objects/<model("aprobacion_proveedores.aprobacion_proveedores"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aprobacion_proveedores.object', {
#             'object': obj
#         })