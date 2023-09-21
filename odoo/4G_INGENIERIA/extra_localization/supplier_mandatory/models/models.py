# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, Warning

class SupplierMandatory(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _onchange_order_line(self):
        if not (self.product_id.seller_ids) and self.product_id.name:
            raise UserError(('Debe configurar al menos un proveedor para el producto'+ self.product_id.name))
            
    @api.onchange('order_line')
    def _onchange_order_line(self):
        if not (self.product_id.seller_ids) and self.product_id.name:
            raise UserError(('Debe configurar al menos un proveedor para el producto'+ self.product_id.name))
            