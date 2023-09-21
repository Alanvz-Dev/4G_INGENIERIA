from odoo import _, api, fields, models


class ReporteNomina(models.Model):
    _name = 'hr_4g_payroll_ext.reporte_nomina'
    _description = '(Inc4G) Reporte'
    _rec_name='nomina'
    name = fields.Char()
    nomina = fields.Many2one('hr.payslip.run')
    incidency_ids = fields.One2many('hr_4g_payroll_ext.incidency','reporte_nomina_ids')
    
    def generar_reporte(self):

        print(self.nomina.slip_ids.mapped('employee_id'))
        empleados_nomina=self.nomina.slip_ids.mapped('employee_id')
        for empleado in empleados_nomina:
            incidency_by_employee=self.incidency_ids.search([('date_from','>=',self.nomina.date_start),('date_to','<=',self.nomina.date_end),('employee_id','in',[empleado.id])])
            nomina = self.nomina.slip_ids.search([('payslip_run_id','in',self.nomina.ids),('contract_id','in',[empleado.contract_id.id])])
            #Unlink solo las que contengan Work 100
            nomina.worked_days_line_ids.search([('payslip_id','in',nomina.ids),('code','in',['WORK100']),('contract_id','in',[empleado.contract_id.id])]).unlink()
            print(nomina)
            for incidency in incidency_by_employee:
                if not incidency.state =='done':
                    print('Raise Error Hay una incidencia no validada')
                if incidency.tipo_incidencia in ['HEX1','HEX2','HEX3','TXT']:                
                    #Excluir las incidencias que no entran en nómina
                    nomina.worked_days_line_ids=[(0, 0, {'name' :incidency.tipo_incidencia, 'code' : incidency.tipo_incidencia, 'contract_id':empleado.contract_id.id, 'number_of_days': abs(incidency.dias),'number_of_hours': abs(incidency.horas_a_considerar)})]
            diass=sum(nomina.worked_days_line_ids.mapped('number_of_days'))
            #Validar que dias sea 7 o no exceda el maximo de faltas
            nomina.worked_days_line_ids=[(0, 0, {'name' :'WORK100', 'code' : 'WORK100', 'contract_id':empleado.contract_id.id, 'number_of_days': 7-diass})]
            print(diass)
        


    @api.onchange('nomina')
    def _onchange_nomina(self):
        self.name=self.nomina.name