# -*- coding: utf-8 -*-

from odoo import fields, models,api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    ford_gsdb = fields.Char(string='GSDB')
