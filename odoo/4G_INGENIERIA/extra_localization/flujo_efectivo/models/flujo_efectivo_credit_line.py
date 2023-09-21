# -*- coding: utf-8 -*-

from odoo import models, fields, api

class credit_line(models.Model):
    _name = 'flujo_efectivo.credit_line'
    date_line_credit = fields.Date(string='Fecha linea de credito', required=True)
    name = fields.Many2one(comodel_name='res.partner', string='Contacto')
    required_amount = fields.Integer(string="Monto", required=True)
    descripcion = fields.Text(string="Nota")
    tipo_credito = fields.Selection([
        ('fact', 'Factoraje'),('lcs', 'Línea de Crédito Simple'),('lcr', 'Linea de Crédito Revolvente')
    ], string='Típo de Crédito')
    fecha_pago = fields.Date(string='Fecha de Pago')
    sub_categoria = fields.Char(string='Subcategorìa')
    

