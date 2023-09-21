# -*- coding: utf-8 -*-
from odoo import http

# class Arrendamiento(http.Controller):
#     @http.route('/arrendamiento/arrendamiento/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/arrendamiento/arrendamiento/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('arrendamiento.listing', {
#             'root': '/arrendamiento/arrendamiento',
#             'objects': http.request.env['arrendamiento.arrendamiento'].search([]),
#         })

#     @http.route('/arrendamiento/arrendamiento/objects/<model("arrendamiento.arrendamiento"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('arrendamiento.object', {
#             'object': obj
#         })