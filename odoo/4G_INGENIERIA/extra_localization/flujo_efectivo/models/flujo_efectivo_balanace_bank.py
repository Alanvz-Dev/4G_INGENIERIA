# -*- coding: utf-8 -*-

from odoo import models, fields, api

class balance_bank(models.Model):
    _name = 'flujo_efectivo.balance_bank'
    date_balance = fields.Date(string='Fecha', required=True)
    name = fields.Many2one(comodel_name='account.journal', string='Banco')
    balance_today = fields.Integer(string="Saldo al día", required = True)
    descripcion = fields.Text(string="Nota")
    sub_categoria = fields.Char(string='Subcategorìa')

    
    
    
    

    
