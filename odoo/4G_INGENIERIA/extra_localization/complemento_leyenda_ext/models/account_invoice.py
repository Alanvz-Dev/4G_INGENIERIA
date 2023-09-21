# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    tax_legend_id = fields.Many2one('complemento_leyenda_ext.tax_legend', string='Complemento de Leyenda')
    
    #Override original method
    @api.model
    def to_json(self):
        res = super(AccountInvoice,self).to_json()

        if self.tax_legend_id:
           res.update({
                'leyendasfiscales10': [{
                      'disposicionFiscal': self.tax_legend_id.tax_provision,
                      'norma': self.tax_legend_id.rule,
                      'textoLeyenda': self.tax_legend_id.legend,
                }]
           })
        return res