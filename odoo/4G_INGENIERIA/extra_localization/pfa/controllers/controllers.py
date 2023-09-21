# -*- coding: utf-8 -*-
from odoo import http

# class Pfa(http.Controller):
#     @http.route('/pfa/pfa/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pfa/pfa/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pfa.listing', {
#             'root': '/pfa/pfa',
#             'objects': http.request.env['pfa.pfa'].search([]),
#         })

#     @http.route('/pfa/pfa/objects/<model("pfa.pfa"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pfa.object', {
#             'object': obj
#         })