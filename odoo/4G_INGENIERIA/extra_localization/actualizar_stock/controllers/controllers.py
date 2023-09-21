# -*- coding: utf-8 -*-
from odoo import http

# class ActualizarStock(http.Controller):
#     @http.route('/actualizar_stock/actualizar_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/actualizar_stock/actualizar_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('actualizar_stock.listing', {
#             'root': '/actualizar_stock/actualizar_stock',
#             'objects': http.request.env['actualizar_stock.actualizar_stock'].search([]),
#         })

#     @http.route('/actualizar_stock/actualizar_stock/objects/<model("actualizar_stock.actualizar_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('actualizar_stock.object', {
#             'object': obj
#         })