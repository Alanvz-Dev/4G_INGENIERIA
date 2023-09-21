# -*- coding: utf-8 -*-
from odoo import http

# class ArchiveContacts4g(http.Controller):
#     @http.route('/archive_contacts_4g/archive_contacts_4g/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/archive_contacts_4g/archive_contacts_4g/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('archive_contacts_4g.listing', {
#             'root': '/archive_contacts_4g/archive_contacts_4g',
#             'objects': http.request.env['archive_contacts_4g.archive_contacts_4g'].search([]),
#         })

#     @http.route('/archive_contacts_4g/archive_contacts_4g/objects/<model("archive_contacts_4g.archive_contacts_4g"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('archive_contacts_4g.object', {
#             'object': obj
#         })