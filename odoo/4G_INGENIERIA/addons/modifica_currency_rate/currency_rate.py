# -*- coding: utf-8 -*-

from odoo import models,fields,api,_


class currency_date(models.Model):
    _name='res.currency.rate'
    _inherit='res.currency.rate'
    tipo_cambio = fields.Float("Tipo de cambio")
    qty_need = fields.Float("Cantidad Necesaria")

	
    @api.append("qty_need")
    def onchange_location_id(self):
        v1 = 0.04406 
        v2 = 22.6945
        tipo_cambio = self.tipo_cambio
        self.qty_need= v1/tipo_cambio*v2
