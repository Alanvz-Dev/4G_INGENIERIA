from odoo import _, api, fields, models


class CfdiTraslado(models.Model):
    _inherit = 'cfdi.traslado'
    cfdi_traslado_account_invoice = fields.Many2one('account.invoice',ondelete='cascade',string="Factura")
    @api.onchange('factura_line_ids')
    def _compute_pesoneto(self):
        peso = 0
        if self.factura_line_ids:
            for line in self.factura_line_ids:
               peso += line.pesoenkg * line.quantity
        self.pesonetototal = peso
