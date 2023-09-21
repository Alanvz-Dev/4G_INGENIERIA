# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseOrderCostos(http.Controller):
#     @http.route('/purchase_order_costos/purchase_order_costos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_order_costos/purchase_order_costos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_order_costos.listing', {
#             'root': '/purchase_order_costos/purchase_order_costos',
#             'objects': http.request.env['purchase_order_costos.purchase_order_costos'].search([]),
#         })

#     @http.route('/purchase_order_costos/purchase_order_costos/objects/<model("purchase_order_costos.purchase_order_costos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_order_costos.object', {
#             'object': obj
#         })