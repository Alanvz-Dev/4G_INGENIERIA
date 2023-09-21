# -*- coding: utf-8 -*-
from odoo import http

# class CuadreBalanza(http.Controller):
#     @http.route('/cuadre_balanza/cuadre_balanza/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cuadre_balanza/cuadre_balanza/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cuadre_balanza.listing', {
#             'root': '/cuadre_balanza/cuadre_balanza',
#             'objects': http.request.env['cuadre_balanza.cuadre_balanza'].search([]),
#         })

#     @http.route('/cuadre_balanza/cuadre_balanza/objects/<model("cuadre_balanza.cuadre_balanza"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cuadre_balanza.object', {
#             'object': obj
#         })