from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import date, datetime, time, timedelta


class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.one
    @api.constrains('partner_id')
    def _update_sale_order_partner_invalid(self):
        if self.partner_id.partner_invalid == True:
            raise UserError(_("El cliente %s, esta inabilitado por falta de informacion contable, favor de revisarlo." % (
                self.partner_id.name)))
