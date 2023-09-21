# -*- coding: utf-8 -*-
from odoo import http

# class Ordenes(http.Controller):
#     @http.route('/ordenes/ordenes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ordenes/ordenes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ordenes.listing', {
#             'root': '/ordenes/ordenes',
#             'objects': http.request.env['ordenes.ordenes'].search([]),
#         })

#     @http.route('/ordenes/ordenes/objects/<model("ordenes.ordenes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ordenes.object', {
#             'object': obj
#         })