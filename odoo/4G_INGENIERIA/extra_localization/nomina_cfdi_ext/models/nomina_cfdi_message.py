from odoo import _, api, fields, models


class hr_wizard(models.TransientModel):
    _name = 'nomina_cfdi.message'
    _description = 'HR employee wizard'
    message = fields.Html(string="Terminado", readonly=True, store=True)
