# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class hr_expense_sheet(models.Model):
    _name='hr.expense.sheet'
    _inherit='hr.expense.sheet'

    bono_paid = fields.Boolean('Bono Pagado')

    finalizado = fields.Boolean('Finalizado')
    comprobado = fields.Boolean('Comprobado')

    bono = fields.Boolean('Bono')
    cantidad_bono=fields.Float(string='Cantidad Bono')
    reference_expense = fields.Many2one('hr.expense', string='Referencia Gasto')



    					
    





