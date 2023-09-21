# -*- coding: utf-8 -*-
from odoo import http

# class CfdiTrasladoExt(http.Controller):
#     @http.route('/cfdi_traslado_ext/cfdi_traslado_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cfdi_traslado_ext/cfdi_traslado_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cfdi_traslado_ext.listing', {
#             'root': '/cfdi_traslado_ext/cfdi_traslado_ext',
#             'objects': http.request.env['cfdi_traslado_ext.cfdi_traslado_ext'].search([]),
#         })

#     @http.route('/cfdi_traslado_ext/cfdi_traslado_ext/objects/<model("cfdi_traslado_ext.cfdi_traslado_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cfdi_traslado_ext.object', {
#             'object': obj
#         })