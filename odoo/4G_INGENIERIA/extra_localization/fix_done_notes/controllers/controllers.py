# -*- coding: utf-8 -*-
from odoo import http

# class FixDoneNotes(http.Controller):
#     @http.route('/fix_done_notes/fix_done_notes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fix_done_notes/fix_done_notes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fix_done_notes.listing', {
#             'root': '/fix_done_notes/fix_done_notes',
#             'objects': http.request.env['fix_done_notes.fix_done_notes'].search([]),
#         })

#     @http.route('/fix_done_notes/fix_done_notes/objects/<model("fix_done_notes.fix_done_notes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fix_done_notes.object', {
#             'object': obj
#         })