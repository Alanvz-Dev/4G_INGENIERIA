# -*- coding: utf-8 -*-
from odoo import http

# class Ferrextool(http.Controller):
#     @http.route('/ferrextool/ferrextool/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ferrextool/ferrextool/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ferrextool.listing', {
#             'root': '/ferrextool/ferrextool',
#             'objects': http.request.env['ferrextool.reports'].search([]),
#         })

#     @http.route('/ferrextool/ferrextool/objects/<model("ferrextool.reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ferrextool.object', {
#             'object': obj
#         })