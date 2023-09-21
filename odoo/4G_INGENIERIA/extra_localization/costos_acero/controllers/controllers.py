# -*- coding: utf-8 -*-
from odoo import http

# class CostosAcero(http.Controller):
#     @http.route('/costos_acero/costos_acero/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/costos_acero/costos_acero/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('costos_acero.listing', {
#             'root': '/costos_acero/costos_acero',
#             'objects': http.request.env['costos_acero.costos_acero'].search([]),
#         })

#     @http.route('/costos_acero/costos_acero/objects/<model("costos_acero.costos_acero"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('costos_acero.object', {
#             'object': obj
#         })