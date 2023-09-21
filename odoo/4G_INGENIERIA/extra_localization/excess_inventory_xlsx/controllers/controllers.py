# -*- coding: utf-8 -*-
from odoo import http

# class ReportesPdf(http.Controller):
#     @http.route('/excess_inventory_xlsx/excess_inventory_xlsx/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/excess_inventory_xlsx/excess_inventory_xlsx/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('excess_inventory_xlsx.listing', {
#             'root': '/excess_inventory_xlsx/excess_inventory_xlsx',
#             'objects': http.request.env['excess_inventory_xlsx.excess_inventory_xlsx'].search([]),
#         })

#     @http.route('/excess_inventory_xlsx/excess_inventory_xlsx/objects/<model("excess_inventory_xlsx.excess_inventory_xlsx"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('excess_inventory_xlsx.object', {
#             'object': obj
#         })