# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class res_partner(models.Model):
    # _name = 'res.partner'
    _inherit = 'res.partner'
    rfc = fields.Char() 
    
class res_users(models.Model):
    # _name = 'res.users'
    _inherit = 'res.users'
    rfc = fields.Char('RFC', related='partner_id.vat', readonly=True)


