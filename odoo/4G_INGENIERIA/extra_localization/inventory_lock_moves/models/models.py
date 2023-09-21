# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
# class inventory_lock_moves(models.Model):
#     _name = 'inventory_lock_moves.inventory_lock_moves'

#     user = fields.Many2one('res.users', string='Usuario con Permiso')






class ProductChangeQuantity(models.TransientModel):
    _inherit = 'stock.change.product.qty'
    @api.model
    def create(self, values):
        inventory_lock_moves_user= self.env['res.users'].has_group('inventory_lock_moves.model_inventory_lock_moves_inventory_lock_moves')
        if inventory_lock_moves_user:
            res = super().create(values)
            print(values)
            if values.get('product_id'):
                values.update(self.onchange_product_id_dict(values['product_id']))
            return super(ProductChangeQuantity, self).create(values)
        else:
            raise UserError(('No esta autorizado para realizar este Ajuste, por favor revisarlo con Contabilidad'))

        
                        

            
            
                    

        
