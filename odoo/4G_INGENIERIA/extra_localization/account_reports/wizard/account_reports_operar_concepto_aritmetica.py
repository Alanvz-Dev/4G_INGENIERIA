# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ModuleName(models.TransientModel):
    _name = 'account_reports.operar_concepto_aritmetica_wizard'
    operar_concepto_id = fields.Many2one('account_reports.operar_concepto')
    aritmetica_de_la_operacion = fields.Selection([
        ('suma', '+'),
        ('resta', '-')],required=True)
    total = fields.Float(digits=(2, 2))