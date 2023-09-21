# -*- coding: utf-8 -*-
from odoo import http

# class NominaCfdiExt(http.Controller):
#     @http.route('/nomina_cfdi_ext/nomina_cfdi_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nomina_cfdi_ext/nomina_cfdi_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nomina_cfdi_ext.listing', {
#             'root': '/nomina_cfdi_ext/nomina_cfdi_ext',
#             'objects': http.request.env['nomina_cfdi_ext.nomina_cfdi_ext'].search([]),
#         })

#     @http.route('/nomina_cfdi_ext/nomina_cfdi_ext/objects/<model("nomina_cfdi_ext.nomina_cfdi_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nomina_cfdi_ext.object', {
#             'object': obj
#         })