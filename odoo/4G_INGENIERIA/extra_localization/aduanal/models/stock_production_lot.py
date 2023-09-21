# -*- coding: utf-8 -*-

from odoo import fields, models,_
#from odoo.exceptions import UserError

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    fecha_pedimento = fields.Date(string=_('Fecha pedimento'))
    num_pedimento = fields.Char(string=_('Número pedimento'))
    lote_serie = fields.Boolean(string=_('Utilizar lotes/serie con pedimento aduanal'))
