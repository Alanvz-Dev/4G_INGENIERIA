from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit ='purchase.order'

    from_mrp_order =  fields.Boolean('Creado desde una Orden de Produccion')