# -*- coding: utf-8 -*-

import string
from odoo import models, fields, api

class vehicular(models.Model):
    _name = 'arrendamiento.vehicular'
    _inherit = 'arrendamiento.arrendamiento'
    _rec_name = 'vehiculo_secuencia'

    observaciones = fields.Text(string="Observaciones", required=False)
    vehiculo_secuencia = fields.Char(string='Folio', default=lambda self: self.env['ir.sequence'].next_by_code('arrendamiento.vehicular'))
    @api.one
    def crear_factura_vehicular(self):
        self.crear_factura()
        pass