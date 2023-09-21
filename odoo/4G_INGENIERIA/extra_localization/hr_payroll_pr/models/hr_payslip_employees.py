# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
#from odoo.addons.hr_payroll.wizard.hr_payroll_payslips_by_employees import HrPayslipEmployees
from datetime import datetime
import time

class HrPayslipEmployeesExt(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        log_rows = ""
        start = time.time()
        # payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(
                active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(
                _("You must select employee(s) to generate payslip(s)."))
        payslip_batch = self.env['hr.payslip.run'].browse(active_id)
        struct_id = payslip_batch.estructura and payslip_batch.estructura.id or False
        other_inputs = []
        for other in payslip_batch.tabla_otras_entradas:
            if other.descripcion and other.codigo:
                other_inputs.append(
                    (0, 0, {'name': other.descripcion, 'code': other.codigo, 'amount': other.monto}))

        for employee in self.web_progress_iter(self.env['hr.employee'].browse(data['employee_ids']), msg="CALCULANDO NÓMINA"):
            try:
                slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False,resumen_nomina_id=self._context['resumen_nomina_id'])
            except:
                slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id,resumen_nomina_id=self.env.context.get('pfa_summary_id'),contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': struct_id or slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id') or employee.contract_id.id,
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
                # Added
                'tipo_nomina': payslip_batch.tipo_nomina,
                'fecha_pago': payslip_batch.fecha_pago,
                'journal_id': payslip_batch.journal_id.id
            }
            if other_inputs and res.get('contract_id'):
                contract_id = res.get('contract_id')
                input_lines = list(other_inputs)
                for line in input_lines:
                    line[2].update({'contract_id': contract_id})
                #input_lines = map(lambda x: x[2].update({'contract_id':contract_id}),input_lines)
                res.update({'input_line_ids': input_lines, })
            res.update({'dias_pagar': payslip_batch.dias_pagar,
                        'imss_dias': payslip_batch.imss_dias,
                        'imss_mes': payslip_batch.imss_mes,
                        'no_nomina': payslip_batch.no_nomina,
                        'mes': '{:02d}'.format(datetime.strptime(to_date, "%Y-%m-%d").month),
                        'isr_devolver': payslip_batch.isr_devolver,
                        'isr_ajustar': payslip_batch.isr_ajustar,
                        'isr_anual': payslip_batch.isr_anual,
                        'concepto_periodico': payslip_batch.concepto_periodico})
            payslip = self.env['hr.payslip']
            payslips = payslip.create(res)
            print(type(payslips))
            if type(payslips) == type(payslip):
                try:
                    payslips.compute_sheet()
                except Exception as error:
                    error_string = str(error)
                    log_rows = log_rows+""" <tr>
    <td>"""+employee.name+"""</td>
    <td>"""+str(payslips)+"""</td>
    <td>"""+str(error_string)+"""</td>
  </tr>"""

            elif isinstance(payslips, str):
                log_rows = log_rows+""" <tr>
    <td>"""+employee.name+"""</td>
    <td>"""+payslips+"""</td>
  </tr>"""

            print(payslips)

        end = time.time()
        print(end - start)
        message = """<!DOCTYPE html>
<html>
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>
</head>
<body>

<h2>Necesita realizar la correción y agregar únicamente a los empleados faltantes para evitar duplicidad de nóminas.</h2>

<table>
  <tr>
    <th>Empleado</th>
    <th>Error</th>
  </tr>"""+log_rows+"""
</table>

</body>
</html>"""

        context_cfdi_traslado = {
            'default_message': message
        }
        payslip_batch.log=message
        return {

            'name': 'Log de posibles errores',

            'type': 'ir.actions.act_window',

            'res_model': 'nomina_cfdi.message',

            'view_mode': 'form',

            'view_type': 'form',

            'target': 'new',
            'context': context_cfdi_traslado

        }

#     @api.multi
#     def compute_sheet(self):
#         res = super(HrPayslipEmployees, self).compute_sheet()
#         active_id = self.env.context.get('active_id')
#         if active_id and self.employee_ids:
#             payslips = self.env['hr.payslip'].search([('employee_id', '=', self.employee_ids.ids), ('payslip_run_id', '=', active_id)])
#             payslip_batch = self.env['hr.payslip.run'].browse(active_id)
#             payslips.write({'tipo_nomina': payslip_batch.tipo_nomina})
#         return res


#HrPayslipEmployees.compute_sheet = HrPayslipEmployeesExt.compute_sheet
