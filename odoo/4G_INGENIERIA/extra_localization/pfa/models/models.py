# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import logging
_logger = logging.getLogger(__name__)

class pfa(models.Model):
    _name = 'pfa.summary'
    name = fields.Char()
    de = fields.Date(string='De')
    al = fields.Date(string='Al')
    fecha_pago = fields.Date()
    pfa_ids = fields.One2many(
        string='pfa',
        comodel_name='pfa.pfa',
        inverse_name='summary_id',
    )

    def create_slip_run(self):


        payslip_run = self.env['hr.payslip.run'].create({
    "tipo_nomina": "E",
    "date_start": self.de,
    "date_end": self.al,
    "journal_id": 49,
    "name": self.name,
    "version_cfdi": "3",
    "fecha_pago": self.fecha_pago,
    "estructura": 38,
    "periodicidad_pago": "99",
    "tipo_configuracion": 1,
    
        })
        
        payslip_run._dias_pagar()
        payslip_run._get_frecuencia_pago()
        payslip_employee = self.env['hr.payslip.employees'].create({
            'employee_ids': [(6,0,self.pfa_ids.mapped('employee_id').ids)]
        })

        payslip_employee.with_context(pfa_summary_id=self.id,active_id=payslip_run.id).compute_sheet()
        
    def create_records(self):
        self.ensure_one()

        hr_contract = self.env['hr.contract']
        employees_ids = hr_contract.search([('employee_id', '!=', False), ('state', 'in', ['open'])]).mapped('employee_id').ids
        for employee in self.web_progress_iter(employees_ids, msg="Calculado Montos") :
            
            base_query = """select hpr.id nomina,hp.id recibo_de_nomina,hp.date_from de,hp.date_to al,hps.id estructura_salarial,sline.amount monto,sline.salary_rule_id regla_salarial,sline.code code from hr_payslip_line sline
inner join hr_payslip hp on sline.slip_id = hp.id
inner join hr_payroll_structure hps on hp.struct_id = hps.id
inner join hr_payslip_run hpr on hp.payslip_run_id  = hpr.id 
where sline.slip_id  in (select id from hr_payslip where employee_id = %s)
and sline.salary_rule_id  in (select id  from hr_salary_rule where code = 'D067')
and (hp.date_from  >= '%s'  AND hp.date_to  <= '%s')
and hp.estado_factura in ('factura_correcta')
order by hp.date_from"""%(employee,self.de,self.al)

            self.env.cr.execute(base_query)
            new_recs = []
            for line in self.env.cr.dictfetchall():
                new_recs.append([0, 0, line])                  
                print(line)
                
        #Create Objects
            self.pfa_ids=[(0, 0, {
    "employee_id":employee,
    "pfa_line_ids":new_recs
            })]


    @api.model
    def create(self, values):
        print(values)
        result = super().create(values)
        return result

    
    

class pfa(models.Model):
    _name = 'pfa.pfa'
    summary_id = fields.Many2one(comodel_name='pfa.summary', string='Resumen')
    employee_id = fields.Many2one(
        string='employee',
        comodel_name='hr.employee',
        ondelete='restrict'
    )
    monto_a_pagar = fields.Float(compute='_compute_monto_a_pagar',string='Monto a Pagar', digits=(16, 2),store=True)
    
    @api.depends('employee_id')
    def _compute_monto_a_pagar(self):
        for record in self:
            record.monto_a_pagar = sum(record.pfa_line_ids.mapped('monto'))
    
    
    recibo_de_nomina = fields.Many2one(comodel_name='hr.payslip', string='Recibo de Nómina')
    pfa_line_ids = fields.One2many(
        string='pfa line',
        comodel_name='pfa.pfa_line',
        inverse_name='pfa_id',
    )

    def get_slips(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Recibos de Nómina",
            "view_mode": "tree,form",
            "res_model": "hr.payslip",
            "domain": [("id", "in", self.pfa_line_ids.mapped('recibo_de_nomina').ids)],
            "context": {'create': False,'edit':False}
        }



class pfa(models.Model):
    _name = 'pfa.pfa_line'
    nomina = fields.Many2one(comodel_name='hr.payslip.run', string='Nomina Origen')
    recibo_de_nomina = fields.Many2one(comodel_name='hr.payslip', string='Recibo de Nómina')
    de = fields.Date(string='De')
    al = fields.Date(string='Al')
    estructura_salarial = fields.Many2one(comodel_name='hr.payroll.structure', string='Estructura Salarial')
    monto = fields.Float(string='Monto', digits=(16, 2))
    regla_salarial = fields.Many2one(comodel_name='hr.salary.rule', string='Regla')
    code = fields.Char(string='Regla Salarial')
    pfa_id = fields.Many2one(comodel_name='pfa.pfa', string='Pfa')




class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    
    @api.model
    def create(self, values):
        print(values)
        result = super().create(values)
        
        return result

    @api.onchange('periodicidad_pago', 'date_start')
    def _get_frecuencia_pago(self):
        if 'active_model' in self._context =='pfa.summary' or 'pfa.summary' in self._context['params']:                       
            delta = datetime.strptime(self.date_end, '%Y-%m-%d') - datetime.strptime(self.date_start, '%Y-%m-%d')
            self.dias_pagar = delta.days
            self.periodicidad_pago="99"
        else:
            values = {}
            if self.date_start and self.dias_pagar:
                fecha_fin = datetime.strptime(self.date_start, '%Y-%m-%d') + relativedelta(days=self.dias_pagar-1)
                if self.periodicidad_pago == '04':
                    if datetime.strptime(self.date_start, '%Y-%m-%d').day > 15:
                        date = datetime.strptime(self.date_start, '%Y-%m-%d')
                        date = date+relativedelta(days=15)
                        month_last_day = monthrange(date.year,date.month)[1]
                        items = [date+relativedelta(day=month_last_day), date+relativedelta(day=15)]
                        previous_month_date = date+relativedelta(months=-1)
                        previous_month_last_day = monthrange(previous_month_date.year,previous_month_date.month)[1]
                        items.append(previous_month_date+relativedelta(day=previous_month_last_day),)
                        if date.day>15:
                            items.append(date+relativedelta(months=1,day=15))
                        fecha_fin = self.nearest_date(items,date)
                values.update({'date_end': fecha_fin})
                self.update(values)





