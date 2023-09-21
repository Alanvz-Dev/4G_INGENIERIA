# -*- coding: utf-8 -*-
from odoo import http

# class FlujoEfectivo(http.Controller):
#     @http.route('/flujo_efectivo/flujo_efectivo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/flujo_efectivo/flujo_efectivo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('flujo_efectivo.listing', {
#             'root': '/flujo_efectivo/flujo_efectivo',
#             'objects': http.request.env['flujo_efectivo.flujo_efectivo'].search([]),
#         })

#     @http.route('/flujo_efectivo/flujo_efectivo/objects/<model("flujo_efectivo.flujo_efectivo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('flujo_efectivo.object', {
#             'object': obj
#         })