# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class account_reports_account_group(models.Model):
    _name = 'account_reports.account_group'
    debito = fields.Float( digits=(16, 2))
    credito = fields.Float( digits=(16, 2))
    saldo_inicial = fields.Float( digits=(16, 2))
    saldo_final = fields.Float( digits=(16, 2))

    cuenta = fields.Many2one('account.group')    
    resultado_considerado = fields.Selection([
        ('initial_balance', 'Saldo Inicial'),
        ('debit', 'Débito'),
        ('credit', 'Crédito'),
        ('final_balance', 'Saldo Final'),
        ('month_moves', 'Movimientos del Mes (Saldo Final- Saldo Inicial)'),
        ('c_d', 'Crédito - Débito'),
        ('d_c', 'Débito - Crédito')
    ],required=True)
    aritmetica_de_la_operacion = fields.Selection([
        ('suma', '+'),
        ('resta', '-')],required=True)
    total = fields.Float( digits=(2, 2))
    concepto_id = fields.Many2one('account_reports.concepto')

    @api.onchange('cuenta')
    def _onchange_cuenta(self):
        if self.cuenta.id:
            search_res = self.concepto_id.report_id.trial_balance_lines.filtered(lambda r: r.account_group_id.id == self.cuenta.id)
            print(search_res)
            self.debito=search_res.debit
            self.credito=search_res.credit
            self.saldo_inicial=search_res.initial_balance
            self.saldo_final=search_res.final_balance
        
    @api.onchange('resultado_considerado','cuenta')
    def _onchange_resultado_considerado(self):
        if self.resultado_considerado=='initial_balance':
            self.total=self.saldo_inicial
        if self.resultado_considerado=='debit':
            self.total=self.debito
        if self.resultado_considerado=='credit':
            self.total=self.credito
        if self.resultado_considerado=='final_balance':
            self.total=self.saldo_final
        if self.resultado_considerado=='month_moves':
            self.total= self.saldo_final-self.saldo_inicial
        if self.resultado_considerado=='c_d':
            self.total=self.credito-self.debito
        if self.resultado_considerado=='d_c':
            self.total=self.debito-self.credito
        

    @api.model
    def create(self, values):
        # CODE HERE
        return super(account_reports_account_group, self).create(values)

    @api.multi
    def write(self, values):
        # CODE HERE
        return super(account_reports_account_group, self).write(values)

        
    


    











