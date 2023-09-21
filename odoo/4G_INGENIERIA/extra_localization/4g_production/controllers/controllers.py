# -*- coding: utf-8 -*-
from odoo import http

# class 4gProduction(http.Controller):
#     @http.route('/4g_production/4g_production/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/4g_production/4g_production/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('4g_production.listing', {
#             'root': '/4g_production/4g_production',
#             'objects': http.request.env['4g_production.4g_production'].search([]),
#         })

#     @http.route('/4g_production/4g_production/objects/<model("4g_production.4g_production"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('4g_production.object', {
#             'object': obj
#         })