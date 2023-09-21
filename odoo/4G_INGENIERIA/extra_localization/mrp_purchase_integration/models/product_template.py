from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit ='product.template'

    analytic_account_id = fields.Many2one('account.analytic.account','Cuenta Analitica')