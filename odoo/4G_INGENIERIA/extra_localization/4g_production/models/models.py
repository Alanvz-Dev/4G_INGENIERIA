# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class 4g_production(models.Model):
#     _name = '4g_production.4g_production'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100