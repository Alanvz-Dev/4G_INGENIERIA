from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class CuentasPorPagarCumplimientoDePago(models.Model):
    _inherit = 'cuentas_por_pagar.cumplimiento_de_pago.model'
    
    @api.model
    def create(self, values):
        # CODE HERE
        partner = self.env['res.partner']        
        if self.env.user.partner_id.parent_id.id:
            partner_id = partner.browse(self.env.user.partner_id.parent_id.id)
        elif self.env.user.partner_id.id:
            partner_id = partner.browse(self.env.user.partner_id.id)
        if partner_id.estado_repse=='draft' or partner_id.estado_repse ==False:
            raise UserError(('El provedor No tiene verificado su registro REPSE'))        
        if partner_id.aplica_repse=='no' or partner_id.aplica_repse==False:
            pass
        
        return super(CuentasPorPagarCumplimientoDePago, self).create(values)