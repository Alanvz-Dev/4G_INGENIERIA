from odoo import _, api, fields, models


class ModuleName(models.Model):
    _inherit = 'mrp.routing.workcenter'

    duracion_estimada = fields.Float(string='Duración Estimada')
