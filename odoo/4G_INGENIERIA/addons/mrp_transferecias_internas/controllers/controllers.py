# -*- coding: utf-8 -*-
from odoo import http

# class MrpTransfereciasInternas(http.Controller):
#     @http.route('/mrp_transferecias_internas/mrp_transferecias_internas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_transferecias_internas/mrp_transferecias_internas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_transferecias_internas.listing', {
#             'root': '/mrp_transferecias_internas/mrp_transferecias_internas',
#             'objects': http.request.env['mrp_transferecias_internas.mrp_transferecias_internas'].search([]),
#         })

#     @http.route('/mrp_transferecias_internas/mrp_transferecias_internas/objects/<model("mrp_transferecias_internas.mrp_transferecias_internas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_transferecias_internas.object', {
#             'object': obj
#         })