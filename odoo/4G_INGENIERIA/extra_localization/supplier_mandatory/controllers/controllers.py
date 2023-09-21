# -*- coding: utf-8 -*-
from odoo import http

# class SupplierMandatory(http.Controller):
#     @http.route('/supplier_mandatory/supplier_mandatory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/supplier_mandatory/supplier_mandatory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('supplier_mandatory.listing', {
#             'root': '/supplier_mandatory/supplier_mandatory',
#             'objects': http.request.env['supplier_mandatory.supplier_mandatory'].search([]),
#         })

#     @http.route('/supplier_mandatory/supplier_mandatory/objects/<model("supplier_mandatory.supplier_mandatory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('supplier_mandatory.object', {
#             'object': obj
#         })