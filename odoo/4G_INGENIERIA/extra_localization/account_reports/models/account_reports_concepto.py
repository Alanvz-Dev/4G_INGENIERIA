# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_reports_concepto(models.Model):
    _name = 'account_reports.concepto'
    _description = 'CONCEPTO'
    _rec_name = 'concepto'
    '''
    Concepto se refiere a un elemento abstracto que representa la operacion aritmética de cuentas
    contables y cuentas agrupadoras
    '''
    concepto = fields.Char()
    resultado_aux = fields.Float(compute='_compute_resultado_aux',string="Resultado")
    report_id = fields.Many2one('account_reports.report')
    account_group_lines = fields.One2many('account_reports.account_group', 'concepto_id')
    account_account_lines = fields.One2many('account_reports.account_account', 'concepto_id')



    @api.model
    def create(self, values):
        # CODE HERE
        return super(account_reports_concepto, self).create(values)

    
    
    @api.one
    @api.depends('account_group_lines','account_account_lines')
    def _compute_resultado_aux(self):
        print(self)
        total_group=0
        total_account=0
        for item in self.account_group_lines:
            if item.aritmetica_de_la_operacion=='suma':
                total_group=total_group+item.total
            if item.aritmetica_de_la_operacion=='resta':
                total_group=total_group-item.total

        for item in self.account_account_lines:
            if item.aritmetica_de_la_operacion=='suma':
                total_account=total_account+item.total
            if item.aritmetica_de_la_operacion=='resta':
                total_account=total_account-item.total
        self.resultado_aux=total_group+total_account

    
