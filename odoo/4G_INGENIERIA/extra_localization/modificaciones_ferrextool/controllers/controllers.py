# -*- coding: utf-8 -*-
from odoo import http

# class ModificacionesFerrextool(http.Controller):
#     @http.route('/modificaciones_ferrextool/modificaciones_ferrextool/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modificaciones_ferrextool/modificaciones_ferrextool/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modificaciones_ferrextool.listing', {
#             'root': '/modificaciones_ferrextool/modificaciones_ferrextool',
#             'objects': http.request.env['modificaciones_ferrextool.modificaciones_ferrextool'].search([]),
#         })

#     @http.route('/modificaciones_ferrextool/modificaciones_ferrextool/objects/<model("modificaciones_ferrextool.modificaciones_ferrextool"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modificaciones_ferrextool.object', {
#             'object': obj
#         })