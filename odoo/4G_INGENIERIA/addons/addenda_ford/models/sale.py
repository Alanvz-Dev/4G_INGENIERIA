# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ford_addenda = fields.Boolean(string='Addenda Ford', default=False)

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'ford_addenda': self.ford_addenda,
                    })
        return invoice_vals