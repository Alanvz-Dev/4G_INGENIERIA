# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lote', copy=False)
    tracking = fields.Selection([('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], related='product_id.tracking', store=True)

    @api.onchange('product_id')
    def _onchange_product_id_set_lot_domain(self):
        available_lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            location = self.order_id.warehouse_id.lot_stock_id
            quants = self.env['stock.quant'].read_group([
                ('product_id', '=', self.product_id.id),
                ('location_id', 'child_of', location.id),
                ('quantity', '>', 0),
                ('lot_id', '!=', False),
            ], ['lot_id'], 'lot_id')
            available_lot_ids = [quant['lot_id'][0] for quant in quants]
        self.lot_id = False
        return {
            'domain': {'lot_id': [('id', 'in', available_lot_ids)]}
        }
    
    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['lot_id'] = self.lot_id.id
        return res
    
#     @api.multi
#     def _prepare_order_line_procurement(self, group_id=False):
#         res = super(
#             SaleOrderLine, self)._prepare_order_line_procurement(
#             group_id=group_id)
#         res['lot_id'] = self.lot_id.id
#         return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_move_from_line(self, line):
        move = self.env['stock.move']
        # i create this counter to check lot's univocity on move line
        lot_count = 0
        for p in line.order_id.picking_ids:
            for m in p.move_lines:
                #if line.lot_id == m.restrict_lot_id:
                if m.move_line_ids.filtered(lambda x:x.lot_id.id==line.lot_id.id):
                    move = m
                    lot_count += 1
                    # if counter is 0 or > 1 means that something goes wrong
                    if lot_count != 1:
                        raise Warning(_('Can\'t retrieve lot on stock'))
        return move

    @api.model
    def _check_move_state(self, line):
        if line.lot_id:
            move = self.get_move_from_line(line)
            if move.state=='draft':
                move._action_confirm()
            if move.state == 'confirmed':
                move._action_assign()
                move.refresh()
            if move.state != 'assigned':
                raise Warning(_('Can\'t reserve products for lot %s') %line.lot_id.name)
        return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        picking = self.env['stock.picking']
        for line in self.order_line:
#             draft_moves = line.move_ids.filtered(lambda x:x.state=='draft')
#             if draft_moves:
#                 draft_moves._action_confirm()
            confirmed_moves = line.move_ids.filtered(lambda move: move.state not in ('cancel', 'done'))
            if confirmed_moves:
                picking += confirmed_moves.mapped('picking_id')
                #confirmed_moves._action_confirm()
            #self._check_move_state(line)
        if picking:
            picking.action_assign()
        return res
