from odoo import _, api, fields, models


class AplicarNomina(models.Model):
    _name = 'hr_4g_payroll_ext.aplicar_nomina'
    _description = '(Inc4G) Aplicar descuentos a Nómina'

    nomina = fields.Many2one('hr.payslip.run')

    def action_ok(self):
        print(self)
        worked_days=self.env['hr.payslip.worked_days']
        print(self._context['active_ids'])
        lines = self.env[self._context['active_model']].browse(self._context['active_ids'])
        for line in lines:
            print(line)
            nomina = self.nomina.slip_ids.search([('payslip_run_id','in',self.nomina.ids),('contract_id','in',[line.employee_id.contract_id.id])])
            if line.tipo_incidencia == 'TXT' and line.dias>0:
                nomina.worked_days_line_ids=[(0, 0, {'name' :'Días Tiempo Por Tiempo', 'code' : line.tipo_incidencia, 'contract_id':line.employee_id.contract_id.id, 'number_of_days': line.dias})]
                print('Separar aqui los tipos')
            if line.tipo_incidencia == 'TXT' and line.dias<0:
                #line.tipo_incidencia
                nomina.worked_days_line_ids=[(0, 0, {'name' :'Descuento Tiempo Por Tiempo', 'code' : 'FI', 'contract_id':line.employee_id.contract_id.id, 'number_of_days': abs(line.dias)})]
                line_worked_days = nomina.worked_days_line_ids.search([('payslip_id','in',nomina.ids),('code','in',['WORK100']),('contract_id','in',[line.employee_id.contract_id.id])])
                for item in line_worked_days:
                    item.number_of_days=item.number_of_days-abs(line.dias)
                    item.number_of_hours=item.number_of_hours-abs(line.horas)
            nomina.line_ids
            for incidency in line.incid_ids:
                incidency.state_pago='done'
                incidency.nomina_de_pago=nomina.id
                print(nomina)
        pass
