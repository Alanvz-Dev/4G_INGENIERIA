from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning


class AsistenteMaterialRequiredInternalLine(models.TransientModel):
    _name = "asistente.material.required.internal.line"
    _description = "Lineas para Requerir Materiales"

    wizard_id = fields.Many2one("asistente.material.required.internal", "ID Retorno")
    qty_need = fields.Float("Cantidad Necesaria", digits=(14, 2))
    qty_reservated = fields.Float("Cantidad Disponible", digits=(14, 2))
    qty_to_transfer = fields.Float("Cantidad a Transferir", digits=(14, 2))
    qty_reservated_in_dest = fields.Float("Cantidad en Produccion", digits=(14, 2))
    product_id = fields.Integer("Producto")
    uom_id = fields.Integer("Unidad de Medida")

    product_id_name = fields.Char("Producto", size=512)
    uom_id_name = fields.Char("Unidad de Medida", size=512)

