# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import pytz


class nomina_semanal(models.Model):
    _name = 'hr_payroll_4g.nomina_semanal'
    departamento = fields.Many2one('hr.department')
    operador = fields.Many2one('hr.employee')
    dia1 = fields.Float()
    dia2 = fields.Float()
    dia3 = fields.Float()
    dia4 = fields.Float()
    dia5 = fields.Float()
    dia6 = fields.Float()
    dia7 = fields.Float()
    bono_asistencia = fields.Boolean()
    bono_puntualidad = fields.Boolean()
    notas = fields.Text()
    incidencias = fields.Text(string='Inc')
    horas_a_pagar = fields.Float()
    nomina_semanal_ids = fields.Many2one(
        'hr_payroll_4g.detalle_nomina_semanal',ondelete='cascade')


class detalle_nomina_semanal(models.Model):
    _name = 'hr_payroll_4g.detalle_nomina_semanal'
    # _rec_name='fecha'
    # fecha = fields.Date()
    # state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho'), ('cancel', 'Cancelado')], string='Estado', default='draft')
    hr_payslip_id = fields.Many2one('hr.payslip.run')
    start_date = fields.Date()
    end_date = fields.Date()
    nombre = fields.Char()
    horas_de_trabajo_id = fields.One2many(
        'hr_payroll_4g.nomina_semanal', 'nomina_semanal_ids')
    active = fields.Boolean(default=True)


    @api.model
    def create(self, vals):
        hr_contract_obj = self.env['hr.contract']
        _detalle_nomina_semanal = super(detalle_nomina_semanal, self).create(vals)
        employee_ids = hr_contract_obj.search([('employee_id','!=',False),('state', '=', 'open')])

        query = "select fecha::date from generate_series('"+str(_detalle_nomina_semanal.start_date)[0:10] + \
            "','" + \
                str(_detalle_nomina_semanal.end_date)[
                    0:10]+"', '1 day'::interval) fecha"
        self.env.cr.execute(query)
        intervalo_de_fechas = self.env.cr.dictfetchall()
        
        for empleado in employee_ids:
            vals = {}
            arr_dias = []
            arr_bono_asitencia = []
            arr_bono_puntualidad = []
            arr_notas=[]
            for dia in intervalo_de_fechas:
                fecha = datetime.strptime(dia.get('fecha'), '%Y-%m-%d')
                fecha_str = str(fecha)[0:10]
                "Trae el recordset del empleado en dada fecha"
                detalle_horas_de_trabajo_nomina = self.env['hr_payroll_4g.detalle_horas_de_trabajo_nomina'].search([('fecha', 'in', [fecha_str])]).id
                if detalle_horas_de_trabajo_nomina:
                    horas_de_trabajo_nomina = self.env['hr_payroll_4g.horas_de_trabajo_nomina'].search([('operador', 'in', [empleado.employee_id.id]), ('horas_de_trabajo_nomina_ids', 'in', [detalle_horas_de_trabajo_nomina])])
                    arr_dias.append(horas_de_trabajo_nomina.horas_a_pagar)
                    if horas_de_trabajo_nomina.nota:
                        arr_notas.append(horas_de_trabajo_nomina.nota)
                    arr_bono_asitencia.append(horas_de_trabajo_nomina.bono_de_asistencia)
                    arr_bono_puntualidad.append(horas_de_trabajo_nomina.bono_de_puntualidad)
                else:
                    arr_dias.append(0.0)
            # Calcular los bonos
            print(self)
            print(_detalle_nomina_semanal.id)
            xc = _detalle_nomina_semanal.id
            incidencias =[]
            vals={}
            hr_horas_de_trabajo = self.env['hr.holidays']
            id_holiday_existente = hr_horas_de_trabajo.get_exists_holiday_list(
                str(_detalle_nomina_semanal.start_date), str(_detalle_nomina_semanal.end_date), empleado.employee_id.id)
            bono_a = True
            bono_p = True
            print(self.start_date)
            query = "select hdtn.bono_de_asistencia ,hdtn.bono_de_puntualidad from hr_payroll_4g_horas_de_trabajo_nomina  hdtn inner join hr_payroll_4g_detalle_horas_de_trabajo_nomina dhdtn on hdtn.horas_de_trabajo_nomina_ids =dhdtn.id where hdtn.operador =" + \
                str(empleado.employee_id.id)+" and dhdtn.fecha in (select i::date from generate_series('" + \
                _detalle_nomina_semanal.start_date+"','" + \
                _detalle_nomina_semanal.end_date+"', '1 day'::interval) i)"
            self.env.cr.execute(query)
            bonos = self.env.cr.dictfetchall()
            print(bonos)
            for bono in bonos:
                if bono.get('bono_de_asistencia') == False:
                    bono_a = False
                if bono.get('bono_de_puntualidad') == False:
                    bono_p = False
            for itemx in id_holiday_existente:
                if itemx.name:
                    incidencias.append(itemx.name)
                    if itemx.name == 'FI':
                        bono_a = False
                        bono_p = False

            if len(incidencias)>=1:
                vals.update({'incidencias':str(incidencias)})

            if len(arr_notas)>=1:
                vals.update({'notas':list(set(arr_notas))})
            print(vals)
            vals.update({
                'nomina_semanal_ids': xc,
                'operador': empleado.employee_id.id,
                'departamento':empleado.employee_id.department_id.id,
                'dia1': arr_dias[0],
                'dia2': arr_dias[1],
                'dia3': arr_dias[2],
                'dia4': arr_dias[3],
                'dia5': arr_dias[4],
                'dia6': arr_dias[5],
                'dia7': arr_dias[6],
                'bono_asistencia': bono_a,
                'bono_puntualidad': bono_p,
                'horas_a_pagar': float(sum(arr_dias))

            })
            self.env['hr_payroll_4g.nomina_semanal'].create(vals)
        return _detalle_nomina_semanal



    @api.onchange('hr_payslip_id')
    def _get_fecha_final(self):
        if self.hr_payslip_id:
            self.start_date = datetime.strptime(self.hr_payslip_id.date_start, '%Y-%m-%d')
            self.end_date = datetime.strptime(self.hr_payslip_id.date_end, '%Y-%m-%d')
        else:
            self.start_date = ''
            self.end_date = ''

    @api.multi
    def action_validar(self):
        if not self.hr_payslip_id.id:
            raise Warning(("Seleccione una nómina por favor"))
        if self.hr_payslip_id.id:
            for item in self.horas_de_trabajo_id:
                contract = self.env['hr.contract'].search([('employee_id','!=',False),('employee_id', '=', item.operador.id)])
                payslip_id = self.env['hr.payslip'].search([('employee_id', '=', item.operador.id), ('payslip_run_id', '=', self.hr_payslip_id.id), ('contract_id', '=', contract.id)])
                try:
                    worked_days = self.env['hr.payslip.worked_days'].search([('payslip_id', '=', payslip_id.id), ('code', '=', 'WORK100')])
                except:
                    raise Warning(("""Empleado duplicado en la nómina.\n
                Por favor asegurese de que el empleado no aparezca más de una vez en la nómina\n.
                Ordene por nombre en la Nómina para encontrar el Empleado Duplicado"""))
                if worked_days:
                    contrato_empleado = self.env['hr.contract'].search([('employee_id','!=',False),('employee_id', '=', item.operador.id)])
                    contrato_empleado.write({'bono_puntualidad': item.bono_puntualidad,'bono_asistencia': item.bono_asistencia})
                    worked_days.update({'number_of_days': ((item.horas_a_pagar*7)/50),'number_of_hours': item.horas_a_pagar})
                if not worked_days:
                    print('No aparece en la nómina')
        return