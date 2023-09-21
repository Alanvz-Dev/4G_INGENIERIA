# -*- coding: utf-8 -*-
from odoo import http

# class AccountMovesLock(http.Controller):
#     @http.route('/account_moves_lock/account_moves_lock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_moves_lock/account_moves_lock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_moves_lock.listing', {
#             'root': '/account_moves_lock/account_moves_lock',
#             'objects': http.request.env['account_moves_lock.account_moves_lock'].search([]),
#         })

#     @http.route('/account_moves_lock/account_moves_lock/objects/<model("account_moves_lock.account_moves_lock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_moves_lock.object', {
#             'object': obj
#         })