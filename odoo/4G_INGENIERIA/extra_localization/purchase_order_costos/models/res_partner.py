from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import date, datetime, time, timedelta


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    partner_invalid = fields.Boolean('Proveedor Invalido para Orden de Compra')
