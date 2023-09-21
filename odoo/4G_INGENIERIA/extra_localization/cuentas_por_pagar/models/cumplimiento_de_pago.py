# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import random


class cumplimiento_pago(models.Model):

    _name = 'cuentas_por_pagar.cumplimiento_de_pago.model'
    _description = 'Cumplimiento de pago'
    #_rec_name='Cumplimiento de Pago'
    @api.model
    def _get_partner(self):
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        return user_br.partner_id.id

    partner_id = fields.Many2one('res.partner', string='Proveedor',
                                 readonly=True, change_default=True,
                                 default=_get_partner)
    rfc = fields.Char('RFC', related='partner_id.vat', readonly=True,
                      size=13)

    @api.one
    @api.depends('rfc')
    def _compute_search_ids(self):
        print('View My Department CLO ACL')
        
    @api.multi
    def search_ids_search1(self,operator,operand):
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        rfc = user_br.partner_id.vat
        partner = self.env['res.partner']
        partner_ids = partner.search([('vat', 'ilike', rfc)]).ids        
        obj = self.env['cuentas_por_pagar.cumplimiento_de_pago.model'].search([('partner_id', '=', partner_ids)]).ids        
        return [('id', 'in', obj)]


    search_ids = fields.Char(
        compute="_compute_search_ids", search='search_ids_search1')

    month = fields.Selection([
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ], string='Mes')

    pdf = fields.Binary(string='Archivo PDF')
    pdfname = fields.Char()





    @api.one
    @api.constrains('pdfname')
    def _check_pdfname(self):
        if self.pdf:
            if not self.pdfname:
                raise UserError(_('No hay Archivo'))
        else:
            tmp = self.pdfname.startswith('.pdf')
            ext = tmp[len(tmp) - 1]
            if ext != 'pdf':
                raise UserError(_('El archivo debe ser PDF'))


