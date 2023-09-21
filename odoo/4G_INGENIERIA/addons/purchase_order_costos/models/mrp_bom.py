from odoo import models, fields, api, _
from datetime import date, datetime, time, timedelta


class mrp_bom(models.Model):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'
    _defaults = {
        'active': False
    }
