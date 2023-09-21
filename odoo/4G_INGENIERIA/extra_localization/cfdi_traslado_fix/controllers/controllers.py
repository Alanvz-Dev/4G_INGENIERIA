# -*- coding: utf-8 -*-
from odoo import http

# class CfdiTrasladoFix(http.Controller):
#     @http.route('/cfdi_traslado_fix/cfdi_traslado_fix/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cfdi_traslado_fix/cfdi_traslado_fix/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cfdi_traslado_fix.listing', {
#             'root': '/cfdi_traslado_fix/cfdi_traslado_fix',
#             'objects': http.request.env['cfdi_traslado_fix.cfdi_traslado_fix'].search([]),
#         })

#     @http.route('/cfdi_traslado_fix/cfdi_traslado_fix/objects/<model("cfdi_traslado_fix.cfdi_traslado_fix"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cfdi_traslado_fix.object', {
#             'object': obj
#         })