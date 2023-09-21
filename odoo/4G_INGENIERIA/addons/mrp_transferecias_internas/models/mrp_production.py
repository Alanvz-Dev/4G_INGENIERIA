from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = "mrp.production"
    last_picking_id = fields.Many2one(
        "stock.picking", "Ultima Solicitud Inventario", readonly=True
    )

