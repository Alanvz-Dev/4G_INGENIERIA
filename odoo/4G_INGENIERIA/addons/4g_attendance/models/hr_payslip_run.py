# -*- coding: utf-8 -*-

from odoo import fields, models, api 

class hr_payslip_extends(models.Model):
    _inherit = 'hr.payslip.run'

    reporte_asistencia = fields.Many2one('reporte.asistencia', string="Reporte Asistencia")

    @api.model
    def action_importar_asistencia(self):
        if self.reporte_asistencia:
            lines = self.reporte_asistencia.mapped('asistencia_line_ids')
            if self.slip_ids:
                for slip_id in self.slip_ids:
                    employee_id = slip_id.employee_id.id
                    emp_line_exist = lines.filtered(lambda x: x.employee_id.id==employee_id)
                    if emp_line_exist:
                        emp_line_exist = emp_line_exist[0]
                        for work_line in slip_id.worked_days_line_ids:
                            if work_line.code == 'WORK100':
                                work_line.update({'number_of_days': emp_line_exist.dias_lab })
                            else:
                                values = {'name': 'Dias laborados',
                                          'code': 'WORK100',
                                          'contract_id': slip_id.contract_id.id,
                                          'number_of_days': emp_line_exist.dias_lab,
                                          'payslip_id': slip_id.id,
                                          'sequence': 10,
                                          }
                                work_line.create(values)
