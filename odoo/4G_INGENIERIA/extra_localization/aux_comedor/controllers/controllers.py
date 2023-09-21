# -*- coding: utf-8 -*-
from odoo import http

# class AuxComedor(http.Controller):
#     @http.route('/aux_comedor/aux_comedor/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aux_comedor/aux_comedor/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aux_comedor.listing', {
#             'root': '/aux_comedor/aux_comedor',
#             'objects': http.request.env['aux_comedor.aux_comedor'].search([]),
#         })

#     @http.route('/aux_comedor/aux_comedor/objects/<model("aux_comedor.aux_comedor"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aux_comedor.object', {
#             'object': obj
#         })