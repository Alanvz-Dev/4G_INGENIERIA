# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date, time, timedelta
import odoo.addons.decimal_precision as dp


class product_template(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    cost_product = fields.Float(string='Costo')

    @api.one
    @api.constrains('standard_price')
    def _cost_product(self):
        coste = self.standard_price
        self.cost_product = coste