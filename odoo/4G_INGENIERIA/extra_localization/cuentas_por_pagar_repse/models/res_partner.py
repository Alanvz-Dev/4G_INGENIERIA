from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class ResPartner(models.Model):
    _inherit = 'res.partner'
    aplica_repse = fields.Selection(selection=[('yes', 'SI'), ('no', 'NO')],default='no')
    estado_repse = fields.Selection(selection=[('done','Validado'), ( 'draft','Faltan Archivos')],default='draft')
    editar_estado_repse = fields.Boolean(compute='set_access_for_repse_partner')

    @api.one
    def set_access_for_repse_partner(self):
        print(self.env['res.users'].has_group('cuentas_por_pagar_repse.group_cuentas_por_pagar_admin'))
        self.editar_estado_repse = self.env['res.users'].has_group('cuentas_por_pagar_repse.group_cuentas_por_pagar_admin')
        if not self.editar_estado_repse:
            self.editar_estado_repse = self.env['res.users'].has_group('cuentas_por_pagar_repse.group_cuentas_por_pagar_usuario_interno')
            



    def get_current_partner_history(self):
        return{
                'name': 'Mis documentos REPSE',
                'view_type': 'form',
                "view_mode": "pivot",
                "view_mode": "tree,form",
                'view_id': False,
                "res_model": "cuentas_por_pagar_repse.history",
                #'views': views,
                'domain': [('partner_id', 'in', self.ids)],
                'type': 'ir.actions.act_window',
            }
