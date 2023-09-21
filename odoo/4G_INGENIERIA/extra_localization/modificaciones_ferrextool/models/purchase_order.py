from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fecha_rfq = fields.Datetime(string="RFQ")
    fecha_oc = fields.Datetime( string="PO")
