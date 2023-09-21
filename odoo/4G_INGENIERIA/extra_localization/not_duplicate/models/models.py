from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def copy(self):
        super().copy() 
        raise UserError("NO PUEDE DUPLICAR ESTE PRODUCTO")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def copy(self):
        super().copy()
        raise UserError("NO PUEDE DUPLICAR ESTE PRODUCTO")

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def copy(self):
        super().copy() 
        raise UserError("NO PUEDE DUPLICAR ESTA FACTURA")

class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.multi
    def copy(self):
        super().copy() 
        raise UserError("NO PUEDE DUPLICAR ESTA CUENTA")
