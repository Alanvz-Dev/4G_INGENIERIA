# -*- coding: utf-8 -*-

from odoo import fields, models,api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    chrysler_no_proveedor = fields.Char(string='No. Proveedor')
