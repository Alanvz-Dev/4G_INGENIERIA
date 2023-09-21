
# -*- coding: utf-8 -*-

from odoo import  models

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super(StockMove,self)._prepare_move_line_vals(quantity, reserved_quant)
        if not vals.get('lot_id') and self.sale_line_id.lot_id:
            vals.update({'lot_id':self.sale_line_id.lot_id.id})
        return vals
    
    def _update_reserved_quantity(self, need, available_quantity, location_id, lot_id=None, package_id=None, owner_id=None, strict=True):
        if self.sale_line_id and self.sale_line_id.lot_id:
            lot_id = self.sale_line_id.lot_id
        return super(StockMove,self)._update_reserved_quantity(need, available_quantity, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
    
#     @api.multi
#     def _prepare_procurement_from_move(self):
#         self.ensure_one()
#         vals = super(StockMove, self)._prepare_procurement_from_move()
#         vals['lot_id'] = self.restrict_lot_id.id
#         return vals
