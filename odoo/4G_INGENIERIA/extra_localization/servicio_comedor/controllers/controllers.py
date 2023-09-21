# -*- coding: utf-8 -*-
from odoo import http

# class ServicioComedor(http.Controller):
#     @http.route('/servicio_comedor/servicio_comedor/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/servicio_comedor/servicio_comedor/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('servicio_comedor.listing', {
#             'root': '/servicio_comedor/servicio_comedor',
#             'objects': http.request.env['servicio_comedor.servicio_comedor'].search([]),
#         })

#     @http.route('/servicio_comedor/servicio_comedor/objects/<model("servicio_comedor.servicio_comedor"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('servicio_comedor.object', {
#             'object': obj
#         })