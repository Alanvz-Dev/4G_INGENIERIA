# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class CfdiTrasladoConfig(models.Model):
    _name = 'cfdi_traslado_ext.config'
    _description = 'Es el valor por defecto para los campos Ubicaciones↳Remitente para el Origen y para Figura Transporte↳Propietarios↳Propietarios'
    _rec_name='contacto_propietario'
    contacto_propietario = fields.Many2one('res.partner', string='Contacto/Propietario',help='Es el valor por defecto para los campos Ubicaciones↳Remitente para el Origen y para Figura Transporte↳Propietarios↳Propietarios')
