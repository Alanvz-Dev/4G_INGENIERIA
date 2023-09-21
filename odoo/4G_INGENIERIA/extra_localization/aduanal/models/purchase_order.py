# -*- coding: utf-8 -*-

from odoo import fields, models, api 

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    compra_con_pedimento = fields.Boolean("Compra con pedimento")
    numero_de_pedimento = fields.Char("Número de pedimento")
    fecha_de_pedimento = fields.Date("Fecha de pedimento")
    
    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        lot_obj = self.env['stock.production.lot']
        for order in self:
            numero_de_pedimento = order.numero_de_pedimento
            if not order.compra_con_pedimento or not numero_de_pedimento:
                continue
            move_lines = order.picking_ids.mapped('move_lines').filtered(lambda x: x.product_id.tracking=='lot')
            for move in move_lines:
                if move.move_line_ids:
                    move_line = move.move_line_ids[0]
                    lot = lot_obj.create({
                            'name' : numero_de_pedimento,
                            'num_pedimento' : numero_de_pedimento,
                            'fecha_pedimento' : order.fecha_de_pedimento,
                            'product_id' : move.product_id.id,
                            })
                    move_line.write({
                        #'qty_done':move_line.product_uom_qty,
                        'lot_name' : numero_de_pedimento,
                        'lot_id' : lot.id,
                        })
                      
#             for line in order.order_line:
#                 if line.product_id.tracking!='lot':
#                     continue
#                 lot = lot_obj.create({
#                     'name' : order.numero_de_pedimento,
#                     'num_pedimento' : order.numero_de_pedimento,
#                     'fecha_pedimento' : order.fecha_de_pedimento,
#                     'product_id' : line.product_id.id,
#                     })
                
        return res