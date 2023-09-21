# -*- coding: utf-8 -*-

import string
from odoo import models, fields, api

class maquinaria(models.Model):
    _name = 'arrendamiento.maquinaria'
    _inherit = 'arrendamiento.arrendamiento'
    _rec_name = 'maquinaria_secuencia'
 
    maquinaria_secuencia = fields.Char(string='Folio', default=lambda self: self.env['ir.sequence'].next_by_code('arrendamiento.maquinaria'))

    @api.one
    def crear_factura_maquinaria(self):
        self.crear_factura()
        pass