# -*- coding: utf-8 -*-
from odoo import http

# class InventoryLockMoves(http.Controller):
#     @http.route('/inventory_lock_moves/inventory_lock_moves/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_lock_moves/inventory_lock_moves/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_lock_moves.listing', {
#             'root': '/inventory_lock_moves/inventory_lock_moves',
#             'objects': http.request.env['inventory_lock_moves.inventory_lock_moves'].search([]),
#         })

#     @http.route('/inventory_lock_moves/inventory_lock_moves/objects/<model("inventory_lock_moves.inventory_lock_moves"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_lock_moves.object', {
#             'object': obj
#         })