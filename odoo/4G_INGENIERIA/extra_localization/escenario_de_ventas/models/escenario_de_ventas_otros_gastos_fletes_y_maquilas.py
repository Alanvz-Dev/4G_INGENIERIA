# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Otros_Gastos_Fletes_Maq(models.Model):
    _name = 'escenario_de_ventas.otros_gastos_fletes_maq'
    _description = 'Otros gatos, fletes y maquilas'

    product_id = fields.Many2one('product.template')
    unidad_de_medida = fields.Many2one('product.uom')
    precio_unitario=fields.Float(digits=(12, 2))
    cantidad= fields.Float(digits=(12, 2))
    total=fields.Float(digits=(12, 2))
    destino = fields.Char()
    notas = fields.Text()
    hoja_de_proyecto = fields.Many2one('escenario_de_ventas.hoja_de_proyecto')


    @api.onchange('product_id','cantidad','precio_unitario')
    def _onchange_product_id(self):
        self.unidad_de_medida=self.product_id.uom_id.id
        self.total = self.precio_unitario*self.cantidad
