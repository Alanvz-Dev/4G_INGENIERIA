from odoo import _, api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    estado_de_entrega = fields.Selection(string='Estatus de Entrega', selection=[('entregado', 'Entregado'), ('noentregado', 'No Entregado')], default='noentregado')
    fecha_de_entrega = fields.Date(string='Fecha de Entrega')
    
    @api.onchange('fecha_de_entrega')
    def _onchange_fecha_de_entrega(self):
        if self.fecha_de_entrega:
            self.estado_de_entrega='entregado'
        if not self.fecha_de_entrega:
            self.estado_de_entrega=False
            self.estado_de_entrega='noentregado'
            
            
