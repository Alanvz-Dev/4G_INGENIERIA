from odoo import _, api, fields, models


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit ='product.product'

    analytic_account_id = fields.Many2one('account.analytic.account','Cuenta Analitica')