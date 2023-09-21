from odoo import models, fields, api
from odoo.exceptions import UserError

class StockPickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = "stock.picking.type"

    route_for_mrp = fields.Boolean("Para Abastecimiento de Produccion", copy=False)

    @api.constrains("route_for_mrp")
    def _constraint_name(self):
        for rec in self:
            if rec.route_for_mrp:
                other_ids = self.search(
                    [("id", "!=", rec.id), ("route_for_mrp", "=", True)]
                )
                if other_ids:
                    raise UserError(
                        (
                            "Error !\nSolo debe existir una Operacion definida para Abastecimiento Interno."
                        )
                    )
        return True
