from odoo import models, fields, api


class mrp_production(models.Model):
    _name = 'mrp.production'
    _inherit = 'mrp.production'
    liberacion_produccion = fields.Boolean('Produccion Liberada')
