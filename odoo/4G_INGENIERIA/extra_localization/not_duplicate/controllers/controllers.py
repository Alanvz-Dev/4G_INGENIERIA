# -*- coding: utf-8 -*-
from odoo import http

# class NotDuplicateProducts(http.Controller):
#     @http.route('/not_duplicate/not_duplicate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/not_duplicate/not_duplicate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('not_duplicate.listing', {
#             'root': '/not_duplicate/not_duplicate',
#             'objects': http.request.env['not_duplicate.not_duplicate'].search([]),
#         })

#     @http.route('/not_duplicate/not_duplicate/objects/<model("not_duplicate.not_duplicate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('not_duplicate.object', {
#             'object': obj
#         })