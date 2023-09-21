# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class aprobacion_proveedores(models.Model):
    _inherit = 'res.partner'

    states = fields.Selection(
        selection=[('draft', 'Borrador'),
                   ('approved', 'Validado')
                   ], string='Product state',
        default='draft',
        help='Estatus de Proveedor.')

    @api.multi
    def button_supplier_approve(self):
        """Product approve"""
        return self.write({'states': 'approved'})

    @api.multi
    def button_supplier_set_to_draft(self):
        """Product set to draft"""
        return self.write({'states': 'draft'})

class aprobacion_proveedores_pago(models.Model):
    _inherit = 'account.payment'

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        # Set partner_id domain
        self.partner_id
        if self.partner_type:
            return {'domain': {'partner_id': [(self.partner_type, '=', True),('states', '=', 'approved')]}}


class aprobacion_proveedores_compras(models.Model):
    _inherit = 'purchase.order'


    @api.constrains('partner_id')
    def _check_partner_id(self):
        # CODE HERE
        if self.partner_id:
            if self.partner_id.states == 'approved':
                pass
            else:
                raise ValidationError(('El proveedor seleccionado no se encuentra validado, pida ayuda al dpto. de Contabilidad o Sistemas.'))                    



class aprobacion_proveedores_pagos(models.Model):
    _inherit = 'account.payment'


    @api.constrains('partner_id')
    def _check_partner_id(self):
        # CODE HERE
        if self.partner_id.supplier:
            if self.partner_id.states == 'approved':
                pass
            else:
                raise ValidationError(('El proveedor seleccionado no se encuentra validado, pida ayuda al dpto. de Contabilidad o Sistemas.\nProveedor: '+self.partner_id.name+'\n',str(self.partner_id.id)))                    
