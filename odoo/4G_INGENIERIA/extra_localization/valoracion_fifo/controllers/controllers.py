# -*- coding: utf-8 -*-
from odoo import http

# class ValoracionFifo(http.Controller):
#     @http.route('/valoracion_fifo/valoracion_fifo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/valoracion_fifo/valoracion_fifo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('valoracion_fifo.listing', {
#             'root': '/valoracion_fifo/valoracion_fifo',
#             'objects': http.request.env['valoracion_fifo.valoracion_fifo'].search([]),
#         })

#     @http.route('/valoracion_fifo/valoracion_fifo/objects/<model("valoracion_fifo.valoracion_fifo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('valoracion_fifo.object', {
#             'object': obj
#         })