# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    date_from_lead = fields.Date("Fecha de cierre")
    no_compra = fields.Char(string='Orden de compra - Cliente')
    #probability = fields.Selection([('high','Alta Probabilidad'),('low','Alta Probabilidad / Orden de Compra'),],'Probabilidad de proyecto')

   