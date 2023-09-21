from odoo import _, api, fields, models


class MrpWorkCenterCapacityMaterial(models.Model):
    _name = 'mrp_workcenter_capacity.material'
    _description = 'Materiales'
    name = fields.Char(string='Material')
