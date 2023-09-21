# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from .sql_server import Get_Axtrax_Attendandce


class axtraxng_attendance(models.Model):
    _name = 'hr.axtraxng_attendance'
    _rec_name = 'hr_payslip_id'

    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho'), ('cancel', 'Cancelado')], string='Estado', default='draft')
    asistencia_line_id = fields.One2many('hr.axtraxng_attendance_line','axtraxng_attendance_ids',string="Reporte Asistencia lines")
    hr_payslip_id = fields.Many2one('hr.payslip.run')

    @api.onchange('hr_payslip_id')
    def _get_fecha_final(self):
        if self.hr_payslip_id:
            self.start_date=datetime.strptime(self.hr_payslip_id.date_start, '%Y-%m-%d')
            self.end_date =datetime.strptime(self.hr_payslip_id.date_end, '%Y-%m-%d')
        else:
            self.start_date=''
            self.end_date = ''

    @api.multi
    def action_validar(self):
        if not self.hr_payslip_id.id:
            raise Warning(_("Seleccione una nómina por favor"))
        if self.hr_payslip_id.id:
            for item in self.asistencia_line_id:
                a=item.employee_id.id
                contract=self.env['hr.contract'].search([('employee_id', '=',a)])
                payslip_id=self.env['hr.payslip'].search([('employee_id', '=',a),('payslip_run_id', '=',self.hr_payslip_id.id),('contract_id','=',contract.id)])
                try:
                    worked_days=self.env['hr.payslip.worked_days'].search([('payslip_id', '=',payslip_id.id),('code', '=','WORK100')])
                except:
                    raise Warning(_("""Empleado duplicado en la nómina.\n
                Por favor asegurese de que el empleado no aparezca más de una vez en la nómina\n.
                Ordene por nombre en la Nómina para encontrar el Empleado Duplicado"""))
                if worked_days:
                    contrato_empleado = self.env['hr.contract'].search([('employee_id', '=',a)])
                    contrato_empleado.write({'bono_puntualidad':item.delay_time_bonus})
                    contrato_empleado.write({'bono_asistencia': item.attendance_bonus})
                    worked_days.update({'number_of_days':((item.horas_trabajadas*7)/50)})
                    worked_days.update({'number_of_hours':item.horas_trabajadas})
                if not worked_days:
                    print('No aparece en la nómina')


        self.write({'state':'done'})
        return

    @api.multi
    def action_cancelar(self):
        self.write({'state':'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state':'draft'})

    def create_axtraxng_attendance1(self):
        if not self.hr_payslip_id:
            raise Warning(_("Seleccione una nómina por favor"))

        fechas_de_nomina = []
        fecha = datetime.strptime(self.start_date, "%Y-%m-%d")
        fechas_de_nomina.append(self.start_date)
        for i in range(6):
            fecha = fecha + timedelta(days=1)
            f1 = str(fecha)
            f = f1[0] + f1[1] + f1[2] + f1[3] + f1[4] + f1[5] + f1[6] + f1[7] + f1[8] + f1[9]
            fechas_de_nomina.append(str(f))
        hr_payslip_employees_ids = self.env['hr.payslip'].search([('payslip_run_id', '=', self.hr_payslip_id.id)]).mapped('employee_id')
        axtraxng_ids=[]
        for item7 in hr_payslip_employees_ids:
            if item7.idaxtraxng>0:
                axtraxng_ids.append(item7)
        for item1 in axtraxng_ids:
            x = str(fechas_de_nomina)
            resultados = []
            for item in fechas_de_nomina:
                try:
                    resultados.append(Get_Axtrax_Attendandce(item1.idaxtraxng, item))
                except:                    
                    resultados.append(['00:00', '00:00', '00', 0, 0])                    
                
            dias_trabajados = 0
            for item3 in range(7):
                hora_entrada = int(resultados[item3][0].split(":")[0])
                minuto_entrada = int(resultados[item3][0].split(":")[1])
                if hora_entrada >0 and hora_entrada <7 and minuto_entrada >0 and minuto_entrada <59:
                    hora_entrada=7
                    minuto_entrada=0
                    print('Entro antes')
                try:
                    print(resultados[item3][1])

                    hora_salida = int(resultados[item3][1].split(":")[0])
                    minuto_salida = int(resultados[item3][1].split(":")[1])
                except:
                    print('##############')
                    print(resultados[item3][1].split(":")[0])
                    print('#########')
                if hora_salida >0 and hora_salida >=17 and minuto_salida>=0:
                    hora_salida=17
                    minuto_salida=0
                    print('Salió despúes')
                dias_trabajados = dias_trabajados + (abs(hora_salida - hora_entrada)) - (
                            abs(minuto_salida - minuto_entrada) / 60)

            faltas = 0
            retardos = 0
            for item4 in resultados:
                retardos = retardos + item4[3]
                faltas = faltas + item4[4]

            bonoa = 1
            bonop = 1
            if retardos >= 1:
                bonop = 0
            if faltas >= 1:
                bonoa = 0
                bonop = 0
            if dias_trabajados>50:
                dias_trabajados=50
            print('Error')
            if self.env['hr.axtraxng_administrative'].search([('employee_id_administrative', '=', item1.id)]):
                faltas=0
                retardos=0
                bonop=1
                bonoa=1
                dias_trabajados=50
            if dias_trabajados<0:
                dias_trabajados=0

            self.env['hr.axtraxng_attendance_line'].create({
                "axtraxng_attendance_ids": self.id,
                'employee_id': item1.id,
                'day1_name': 'Viernes',
                'day2_name': 'Sábado',
                'day3_name': 'Domingo',
                'day4_name': 'Lunes',
                'day5_name': 'Martes',
                'day6_name': 'Miércoles',
                'day7_name': 'Jueves',

                'day1_in': resultados[0][0],
                'day2_in': resultados[1][0],
                'day3_in': resultados[2][0],
                'day4_in': resultados[3][0],
                'day5_in': resultados[4][0],
                'day6_in': resultados[5][0],
                'day7_in': resultados[6][0],

                'day1_out': resultados[0][1],
                'day2_out': resultados[1][1],
                'day3_out': resultados[2][1],
                'day4_out': resultados[3][1],
                'day5_out': resultados[4][1],
                'day6_out': resultados[5][1],
                'day7_out': resultados[6][1],

                'day1_effective_time': resultados[0][2],
                'day2_effective_time': resultados[1][2],
                'day3_effective_time': resultados[2][2],
                'day4_effective_time': resultados[3][2],
                'day5_effective_time': resultados[4][2],
                'day6_effective_time': resultados[5][2],
                'day7_effective_time': resultados[6][2],
                'absence': faltas,
                'delay_time': retardos,
                'attendance_bonus': bonoa,
                'delay_time_bonus': bonop,
                'horas_trabajadas': dias_trabajados
            })













