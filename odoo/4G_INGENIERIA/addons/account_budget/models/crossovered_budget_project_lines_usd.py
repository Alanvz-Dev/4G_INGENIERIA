# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime

class CrossoveredBudgetLinesProjectUSD(models.Model):
    _name = "crossovered.budget.project.lines.usd"
    _description = "Budget Line"

    crossovered_budget_id = fields.Many2one(
        'crossovered.budget.project', 'Presupuesto', ondelete='cascade', index=True, required=True)
    # analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    responsible_employee = fields.Many2one(
        'res.users', 'Responsable de la Cuenta')
    general_budget_id = fields.Many2one('account.budget.post.project', 'Posición Presupuestaria', required=True)
    paid_date = fields.Date('Fecha de Pago')        
    practical_amount2 = fields.Float(
        compute='_compute_percentage_usd', string='Logro')
    company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company',
                                 string='Company', store=True, readonly=True)



    currency_line = fields.Many2one('res.currency', 'Moneda')



    planned_amount = fields.Float('Importe Planeado', required=True, )
    planned_amount_usd = fields.Float(compute="_compute_planned_amount_mxn",string='Importe Planeado USD', required=True, digits=(10,4))
    planned_amount_mxn = fields.Float(compute="_compute_planned_amount_mxn",string ='Importe Planeado MXN', required=True, digits=(10,4))

    practical_amount = fields.Float(compute='_compute_practical_amount_usd', string='Importe Real MXN', digits=(10,4))
    practical_amount_mxn = fields.Float(compute='_compute_practical_amount_mxn', string='Importe Real MXN', digits=(10,4))    
    practical_amount_usd = fields.Float(compute='_compute_practical_amount_mxn', string='Importe Real USD', digits=(10,4))    

    @api.one
    @api.depends('practical_amount')
    def _compute_practical_amount_mxn(self):
        horas_mano_de_obra=0
        if self.general_budget_id.id == 3 or self.general_budget_id.name=="MANO DE OBRA":            
            proyecto1="select sum(hc.sueldo_integrado * (mayord.day1_name/9.5)) from hr_contract hc inner join hr_payroll_4g_horas_de_trabajo mayord on hc.employee_id = mayord.operador where mayord.proyecto1 = "+str(self.crossovered_budget_id.name.id)
            proyecto2="select sum(hc.sueldo_integrado * (mayord.day2_name/9.5)) from hr_contract hc inner join hr_payroll_4g_horas_de_trabajo mayord on hc.employee_id = mayord.operador where mayord.proyecto2 = "+str(self.crossovered_budget_id.name.id)
            proyecto3="select sum(hc.sueldo_integrado * (mayord.day3_name/9.5)) from hr_contract hc inner join hr_payroll_4g_horas_de_trabajo mayord on hc.employee_id = mayord.operador where mayord.proyecto3 = "+str(self.crossovered_budget_id.name.id)
            proyecto4="select sum(hc.sueldo_integrado * (mayord.day4_name/9.5)) from hr_contract hc inner join hr_payroll_4g_horas_de_trabajo mayord on hc.employee_id = mayord.operador where mayord.proyecto4 = "+str(self.crossovered_budget_id.name.id)
            self.env.cr.execute(proyecto1)
            total_proyecto1=(self.env.cr.fetchall()[0][0] or 0)
            
            self.env.cr.execute(proyecto2)
            total_proyecto2=(self.env.cr.fetchall()[0][0] or 0)
            
            self.env.cr.execute(proyecto3)
            total_proyecto3=(self.env.cr.fetchall()[0][0] or 0)   
            
            self.env.cr.execute(proyecto4)
            total_proyecto4=(self.env.cr.fetchall()[0][0] or 0)   
        
            horas_mano_de_obra=(-(total_proyecto1+total_proyecto2+total_proyecto3+total_proyecto4))
            horas_mano_de_obra=0
            ##################################
            horas_proyecto = sum(self.env['hr_payroll_pr.horas_proyecto'].search([('analytic_account_id','in',self.crossovered_budget_id.name.ids)]).mapped('monto'))
            print(horas_proyecto)
            y = (self.practical_amount +horas_mano_de_obra)
            print(y)
            ##################################
            self.practical_amount=(self.practical_amount +horas_mano_de_obra) + -1*(abs(horas_proyecto))
            
        #Practical amount siempre va a estar en pesos
        if self.currency_line.name=='MXN':
            self.practical_amount_mxn=float(self.practical_amount)
            try:
                print(float(self.practical_amount/self.crossovered_budget_id.computado))
                self.practical_amount_usd=float(self.practical_amount/self.crossovered_budget_id.computado)
            except:
                self.practical_amount_usd=0.0
        if self.currency_line.name=='USD':            
            try:
                self.practical_amount_usd=float(self.practical_amount/(self.crossovered_budget_id.computado))
                self.practical_amount_mxn =float(self.practical_amount)
            except:
                self.practical_amount_usd=0.0

#sueldo_integrado  
    @api.one
    @api.depends('planned_amount')
    def _compute_planned_amount_mxn(self):        
        if self.currency_line.name=='MXN':
            try:
                self.planned_amount_usd=float(self.planned_amount)/float(self.crossovered_budget_id.computado)
                self.planned_amount_mxn=float(self.planned_amount            )
            except:
                self.planned_amount_usd=0.0000
                self.planned_amount_mxn=0.0000

        if self.currency_line.name=='USD':
            try:
                self.planned_amount_mxn=float(self.planned_amount*self.crossovered_budget_id.computado)
                self.planned_amount_usd=float(self.planned_amount)
            except:
                self.planned_amount_mxn=0.0000
                self.planned_amount_usd=0.0000


    @api.multi
    def _compute_percentage_usd(self):
        # crossovered.budget.project.lines(1,)

        for line in self:
            if line.practical_amount_mxn != 0.00:
                print("Real"+str(line.practical_amount_mxn))
                print("Planeado"+str(line.planned_amount_mxn))
                try:
                    line.practical_amount2 = abs(float(
                        (line.practical_amount_mxn*100)/line.planned_amount_mxn))
                    print(line.practical_amount2)
                except:
                    line.practical_amount2 = 0.0
            else:
                line.practical_amount2 = 0.00

    @api.one
    def _compute_practical_amount_usd(self):

        print(self)
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            acc_ids_str = ""
            if line.crossovered_budget_id.name.id:
                for item in acc_ids:
                    acc_ids_str = acc_ids_str+str(item)+','
                acc_ids_str = acc_ids_str.rstrip(acc_ids_str[-1])
            try:
                general_budget = self.env['account.move.line'].search(
                    [('contabilidad_electronica', '=','True'),('analytic_account_id', '=', line.crossovered_budget_id.name.id), ('account_id', 'in', acc_ids)])
                for item in general_budget:
                    if item.move_id.state=='posted':
                        result = float(result+item.credit-item.debit)
            except:
                result = 0.0
        
        line.practical_amount=result

    @api.multi
    def open_record(self):
        account_move_lines_filtered=[]
        print(self)
        account_move_lines = self.env['account.move.line'].search(
            [('contabilidad_electronica', '=','True'),('analytic_account_id', '=', self.crossovered_budget_id.name.id), ('account_id', 'in', self.general_budget_id.account_ids.ids)])
        for item in account_move_lines:
            if item.move_id.state=='posted':
                account_move_lines_filtered.append(item.id)        
        return {
            'name': 'Movimientos de: '+self.general_budget_id.display_name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', account_move_lines_filtered)],
            'target': 'current'
        }
