from odoo import _, api, fields, models


class AsistenteMaterialRequiredLine(models.TransientModel):
    _name = 'asistente.material.required.line'
    _description = 'Lineas para Requerir Materiales'

    wizard_id = fields.Many2one('asistente.material.required', 'ID Retorno')
    product_id = fields.Many2one('product.product','Producto')
    uom_id = fields.Many2one('product.uom','Unidad de Medida')
    qty_need = fields.Float('Cantidad Necesaria', digits=(14,2))
    qty_reservated = fields.Float('Cantidad No Reservada', digits=(14,2))
    qty_to_purchase = fields.Float('Cantidad a Comprar', digits=(14,2))
    product_wo_supplier = fields.Boolean('Sin Proveedor', help='Indica que el Producto no contiene un Proveedor', )
    product_wo_supplier_id = fields.Many2one('product.supplierinfo','Proveedor del producto')

