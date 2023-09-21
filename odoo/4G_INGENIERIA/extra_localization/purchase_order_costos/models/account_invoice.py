# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class account_invoice(models.Model):
    _name = 'account.invoice'

    reference=fields.Integer(string='Referencia Factura', readonly=True)
   
    @api.onchange('reference')
    def _onchange_reference_id(self):
        if self.id:
      	    self.expense_id=self.id
	    #self.env.cr.execute(" UPDATE hr_expense SET expense_id=%s WHERE id=%s" % (self.id,self.id))
    