# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo import _, api, fields, models


class ResPertner(models.Model):
    _inherit = 'res.partner'

    cce_licencia = fields.Char(string=_('No. licencia'))
