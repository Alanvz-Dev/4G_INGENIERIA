from odoo import _, api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _sql_constraints = [
        ('barcode_dinning_service', 'unique(barcode_dinning_service)',
         'barcode_dinning_service already exists!')
    ]
    barcode_dinning_service = fields.Float()
    services_count = fields.Float()
