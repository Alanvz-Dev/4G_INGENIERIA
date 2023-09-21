# -*- coding: utf-8 -*-

from odoo import models, fields, api

class production_time(models.Model):
    _name = 'production_time.production_time'

    producto = fields.Many2one('product.product')
    fecha_programada = fields.Date()
    piezas_x_dia = fields.Float()
    horas_x_dia = fields.Float()

    def test(self):
        print('Hola Hola')
        print('Hola Hola')
        print('Hola Hola')
        print('Hola Hola')
        print('Hola Hola')
        print('Hola Hola')
        print('Hola Hola')
        print('Hola Hola')
    
