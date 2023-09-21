# -*- coding: utf-8 -*-
from odoo import http

# class CrearCategorias(http.Controller):
#     @http.route('/crear_categorias/crear_categorias/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crear_categorias/crear_categorias/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crear_categorias.listing', {
#             'root': '/crear_categorias/crear_categorias',
#             'objects': http.request.env['crear_categorias.crear_categorias'].search([]),
#         })

#     @http.route('/crear_categorias/crear_categorias/objects/<model("crear_categorias.crear_categorias"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crear_categorias.object', {
#             'object': obj
#         })