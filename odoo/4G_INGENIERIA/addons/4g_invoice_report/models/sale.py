# -*- coding: utf-8 -*-

from odoo import fields, models, api,_ 

class SaleOrder(models.Model):
    _inherit = 'sale.order'
	
    no_compra = fields.Char('Orden de compra cliente')
