from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fecha_rfq = fields.Datetime(string="Fecha Envío:")
    # fecha_oc = fields.Datetime( string="Fecha Recepción:")
    fecha_oc = fields.Datetime(compute='_compute_fecha_oc', string='Fecha Recepción:')
    
    def _compute_fecha_oc(self):
        for item in self:
            crm = self.env['crm.lead'].search([('order_ids','in',item.ids)])
            item.fecha_oc = crm.create_date or False



    
    