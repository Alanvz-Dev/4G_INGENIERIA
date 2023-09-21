# -*- coding: utf-8 -*-
from odoo import http

# class CuentasPorPagar(http.Controller):
#     @http.route('/cuentas_por_pagar/cuentas_por_pagar/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cuentas_por_pagar/cuentas_por_pagar/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cuentas_por_pagar.listing', {
#             'root': '/cuentas_por_pagar/cuentas_por_pagar',
#             'objects': http.request.env['cuentas_por_pagar.cuentas_por_pagar'].search([]),
#         })

#     @http.route('/cuentas_por_pagar/cuentas_por_pagar/objects/<model("cuentas_por_pagar.cuentas_por_pagar"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cuentas_por_pagar.object', {
#             'object': obj
#         })