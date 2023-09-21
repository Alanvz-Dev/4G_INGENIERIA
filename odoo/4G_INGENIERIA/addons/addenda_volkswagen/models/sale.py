# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class  ContactoVw(models.Model):
    _name = 'addenda.vw.contacto'
    _rec_name = 'contacto_nombre'

    contacto_direccion = fields.Char("Direccion")
    contacto_nombre = fields.Char("Nombre de contacto")
    contacto_mail = fields.Char("Direccion e-mail de Contacto")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vw_posicion = fields.Char(string='No. Posicion VW')
    vw_odc = fields.Char(string='Orden de compra VW')
    vw_contacto = fields.Many2one('addenda.vw.contacto', string='Contacto Addenda')
    vw_notas = fields.Char(string='Notas VW')
    vw_pdf = fields.Binary(string=_('Remision PDF'))
    vw_addenda = fields.Boolean(string='Addenda VW')

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'vw_addenda': self.vw_addenda,
                             'vw_pdf': self.vw_pdf,
                             'vw_notas': self.vw_notas,
                             'vw_contacto': self.vw_contacto.id,
                             'vw_posicion': self.vw_posicion,
                    })
        return invoice_vals