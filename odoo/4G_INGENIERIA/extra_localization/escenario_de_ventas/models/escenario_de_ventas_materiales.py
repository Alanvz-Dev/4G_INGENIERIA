# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api
import math

class escenario_de_ventas(models.Model):
    _name = 'escenario_de_ventas.materiales'
    _description = 'Estimacion de los materiales para el proyecto (PRESUPUESTO)'

    product_id = fields.Many2one('product.template',copy=True)
    unidad_de_medida = fields.Many2one('product.uom',copy=True)
    cantidad_x_pieza = fields.Float(digits=(12, 4),copy=True)
    categoria = fields.Many2one('product.category',copy=True)
    porcentaje_de_scrap = fields.Float(copy=True)
    cantidad_total = fields.Float(copy=True)
    precio_unitario = fields.Float(copy=True)
    total = fields.Float(copy=True)
    peso = fields.Float(copy=True)
    peso_total = fields.Float(copy=True)
    attachment = fields.Binary(string="Attachment",copy=True)
    store_fname = fields.Char(string="File Name",copy=True)
    hoja_de_proyecto = fields.Many2one('escenario_de_ventas.hoja_de_proyecto',copy=True)
    personalizar_registro = fields.Boolean(string='Personalizar Registro',copy=True)

    @api.onchange('product_id','cantidad_x_pieza', 'porcentaje_de_scrap','precio_unitario')
    def _onchange_product_id(self):
        if not self.precio_unitario > 0.0:
            self.precio_unitario=self.product_id.cost_product            
        if not self.categoria:
            self.categoria=self.product_id.categ_id.id
        if not self.unidad_de_medida:
            self.unidad_de_medida=self.product_id.uom_id.id
        self.cantidad_total=self.cantidad_x_pieza*self.hoja_de_proyecto.total_piezas
        if not self.peso>0:
            self.peso=self.product_id.weight
        if self.porcentaje_de_scrap >= 1:
            self.cantidad_total = math.ceil(self.cantidad_x_pieza*self.hoja_de_proyecto.total_piezas + \
                (self.cantidad_x_pieza*self.hoja_de_proyecto.total_piezas *
                 self.porcentaje_de_scrap)/100)
        else:
            self.cantidad_total = math.ceil(self.cantidad_x_pieza*self.hoja_de_proyecto.total_piezas)
        self.total = self.precio_unitario*self.cantidad_total
        self.peso_total=self.product_id.weight*self.cantidad_total*self.hoja_de_proyecto.total_piezas    








            