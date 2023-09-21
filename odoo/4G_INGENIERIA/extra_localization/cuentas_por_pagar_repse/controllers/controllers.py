# -*- coding: utf-8 -*-
from odoo import http

# class CuentasPorPagarRepse(http.Controller):
#     @http.route('/cuentas_por_pagar_repse/cuentas_por_pagar_repse/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cuentas_por_pagar_repse/cuentas_por_pagar_repse/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cuentas_por_pagar_repse.listing', {
#             'root': '/cuentas_por_pagar_repse/cuentas_por_pagar_repse',
#             'objects': http.request.env['cuentas_por_pagar_repse.cuentas_por_pagar_repse'].search([]),
#         })

#     @http.route('/cuentas_por_pagar_repse/cuentas_por_pagar_repse/objects/<model("cuentas_por_pagar_repse.cuentas_por_pagar_repse"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cuentas_por_pagar_repse.object', {
#             'object': obj
#         })