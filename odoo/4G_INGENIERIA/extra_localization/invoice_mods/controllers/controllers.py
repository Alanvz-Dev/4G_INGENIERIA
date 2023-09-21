# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceMods(http.Controller):
#     @http.route('/invoice_mods/invoice_mods/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_mods/invoice_mods/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_mods.listing', {
#             'root': '/invoice_mods/invoice_mods',
#             'objects': http.request.env['invoice_mods.invoice_mods'].search([]),
#         })

#     @http.route('/invoice_mods/invoice_mods/objects/<model("invoice_mods.invoice_mods"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_mods.object', {
#             'object': obj
#         })