# -*- coding: utf-8 -*-

from odoo import models, fields, api

class aux_comedor(models.Model):
     _inherit = 'hr.contract'

     aux_service_count = fields.Integer()


