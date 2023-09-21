from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    amount_pending_delivery = fields.Float(compute='_compute_amount_pending_delivery', string='Pendiente por Entregar')
    amount_pending_delivery_st = fields.Float()
    @api.one
    def _compute_amount_pending_delivery(self):
        amount=0
        for line in self.order_line:
            amount =amount + (line.product_uom_qty-line.qty_delivered)*(line.price_unit)
        self.amount_pending_delivery=amount
        self.amount_pending_delivery_st=amount
        self.write({'amount_pending_delivery_st':amount})
        self.update({'amount_pending_delivery_st':amount})
        print(self)