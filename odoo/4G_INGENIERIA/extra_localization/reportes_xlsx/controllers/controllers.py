# -*- coding: utf-8 -*-
from odoo import http

# class ReportesPdf(http.Controller):
#     @http.route('/reportes_xlsx/reportes_xlsx/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reportes_xlsx/reportes_xlsx/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reportes_xlsx.listing', {
#             'root': '/reportes_xlsx/reportes_xlsx',
#             'objects': http.request.env['reportes_xlsx.reportes_xlsx'].search([]),
#         })

#     @http.route('/reportes_xlsx/reportes_xlsx/objects/<model("reportes_xlsx.reportes_xlsx"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reportes_xlsx.object', {
#             'object': obj
#         })