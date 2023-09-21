# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
	
    leyenda = fields.Boolean(string='Leyenda', default=False)

    @api.model
    def to_json(self):
        res = super(AccountInvoice,self).to_json()

        if self.leyenda:
           res.update({
                'leyendasfiscales10': [{
                      'disposicionFiscal': self.company_id.disposicionfiscal,
                      'norma': self.company_id.norma,
                      'textoLeyenda': self.company_id.textoleyenda,
                }]
           })
        return res
