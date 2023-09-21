# -*- coding: utf-8 -*-
from odoo import http

# class ComplementoLeyendaExt(http.Controller):
#     @http.route('/complemento_leyenda_ext/complemento_leyenda_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/complemento_leyenda_ext/complemento_leyenda_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('complemento_leyenda_ext.listing', {
#             'root': '/complemento_leyenda_ext/complemento_leyenda_ext',
#             'objects': http.request.env['complemento_leyenda_ext.complemento_leyenda_ext'].search([]),
#         })

#     @http.route('/complemento_leyenda_ext/complemento_leyenda_ext/objects/<model("complemento_leyenda_ext.complemento_leyenda_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('complemento_leyenda_ext.object', {
#             'object': obj
#         })