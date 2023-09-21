import string
from odoo import _, api, fields, models


class InOut(models.Model):
    _name = 'hr_4g_payroll_ext.in_out_guard'
    _description = '(Inc4G) Entrada y Salida Guardia'

    date_in = fields.Datetime(track_visibility='onchange',string = 'Entrada')
    date_out = fields.Datetime(track_visibility='onchange',string = 'Salida')
