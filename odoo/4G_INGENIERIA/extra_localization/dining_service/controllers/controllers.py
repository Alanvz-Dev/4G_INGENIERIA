# -*- coding: utf-8 -*-
from odoo import http

# class DiningService(http.Controller):
#     @http.route('/dining_service/dining_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dining_service/dining_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dining_service.listing', {
#             'root': '/dining_service/dining_service',
#             'objects': http.request.env['dining_service.dining_service'].search([]),
#         })

#     @http.route('/dining_service/dining_service/objects/<model("dining_service.dining_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dining_service.object', {
#             'object': obj
#         })