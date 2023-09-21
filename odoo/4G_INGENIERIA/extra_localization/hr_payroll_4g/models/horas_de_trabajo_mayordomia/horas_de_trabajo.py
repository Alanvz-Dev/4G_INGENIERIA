# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime   
import pytz

class horas_de_trabajo(models.Model):
    _name = 'hr_payroll_4g.horas_de_trabajo'
    _rec_name = 'operador'
    departamento = fields.Many2one('hr.department')
    operador = fields.Many2one('hr.employee')
    detalle_horas_de_trabajo_ids = fields.Many2one('hr_payroll_4g.detalle_horas_de_trabajo',ondelete='cascade')
    proyecto1 = fields.Many2one('account.analytic.account')
    day1_name = fields.Float('Duración en Horas')
    proyecto2 = fields.Many2one('account.analytic.account')
    day2_name = fields.Float('Duración en Horas')
    proyecto3 = fields.Many2one('account.analytic.account')
    day3_name = fields.Float('Duración en Horas')
    proyecto4 = fields.Many2one('account.analytic.account')
    day4_name = fields.Float('Duración en Horas')
    balance_de_horas = fields.Float('Balance de Horas')
    incidencia = fields.Selection([
        ('WORK_100', 'A'),
        ('PER', 'P'),
        ('FJC', 'FJC'),
        ('FJS', 'FJS'),
        ('FI', 'FI'),
        ('FR', 'FR'),
        ('VAC', 'VAC'),
        ('INC_RT', 'INC_RT'),
        ('INC_EG', 'INC_EG'),
        ('INC_MAT', 'INC_MAT')], 'Type', default='WORK_100')
    incidencia_id = fields.Many2one('resource.calendar.leaves')
    incidencia_id_holidays = fields.Many2one('hr.holidays')
    read_only = fields.Boolean(default=False)
    fuera_de_planta = fields.Boolean(default=False)
    total_de_horas = fields.Float('Total de Horas', compute='get_total_de_horas', digits=(12, 2), store=True)

    @api.depends('day1_name', 'day2_name', 'day3_name', 'day4_name')
    def get_total_de_horas(self):
            for item in self:
                item.total_de_horas = float(
                    item.day1_name+item.day2_name+item.day3_name+item.day4_name)

    

    @api.depends('operador')
    def _get_division_id(self):
        print(self)
        if len(self) == 1:
            detalle_horas_de_trabajo = self.env['hr_payroll_4g.detalle_horas_de_trabajo'].browse(
                self.detalle_horas_de_trabajo_ids.id)
            contrato_de_operador = self.env['hr_payroll_4g.operador'].browse(
                self.operador.id)
            consulta_de_incidencia = self.env['hr_payroll_4g.incidencia'].search(
                [('empleado_de_la_incidencia', '=', contrato_de_operador.empleado.id), ('fecha_de_la_incidencia', '=', detalle_horas_de_trabajo.fecha)])
            if consulta_de_incidencia.id:
                self.incidencia = consulta_de_incidencia.id

    @api.onchange('incidencia')
    def on_change_state(self):
        if not self.incidencia:
            raise UserError(
                ('Por favor agregue una Incidencia Válida'))
        if not self.incidencia_id_holidays.state == 'validate':
            holidays_obj=self.env['hr.holidays']
            horas_de_trabajo_valss = {}
            holidays_vals = {}
            resource_calendar_vals = {}
            incidencias_list=['FJS','FJC', 'FI', 'FR', 'VAC', 'INC_RT', 'INC_EG', 'INC_MAT']
            resource_calendar_vals.update(
                {'resource_id': self.operador.resource_id.id,
                 'date_from':str(holidays_obj.local_to_utc(self.detalle_horas_de_trabajo_ids.fecha+' 07:00:00')).replace("+00:00", ""),
                 'date_to': str(holidays_obj.local_to_utc(self.detalle_horas_de_trabajo_ids.fecha+' 17:00:00')).replace("+00:00", "")
                 })
            
            horas_de_trabajo_valss.update({
                'incidencia': self.incidencia,
                'operador': self.operador.id,
                'departamento':self.departamento.id,
            })

            holidays_vals.update({'employee_id': self.operador.id,
                                  'date_from': resource_calendar_vals.get('date_from'),
                                  'date_to': resource_calendar_vals.get('date_to'),
                                  'number_of_days_temp':1.4,
                                  'number_of_days':-1.4})
            x= self.incidencia_id_holidays.id
            self.env['resource.calendar.leaves'].search([('holiday_id', 'in', [x])]).unlink()
            holidays_obj.search([('id', 'in', [x])]).unlink()
                

            if self.incidencia in incidencias_list:
                horas_de_trabajo_valss.update({
                    'incidencia': self.incidencia,                   
                    "day1_name": 0,
                    "day2_name": 0,
                    "day3_name": 0,
                    "day4_name": 0,

                })

                status_id = self.env['hr.holidays.status'].search([('name','=',horas_de_trabajo_valss.get('incidencia'))])
                if len(status_id)>1:
                    raise UserError(
                    ('La Incidencia existe más de una vez, por favor asegurese de tener valores únicos'))

                holidays_vals.update({'holiday_status_id': status_id.id,'name': horas_de_trabajo_valss.get('incidencia'),'state': 'confirm'})
                created_holidays = holidays_obj.create(holidays_vals)

                horas_de_trabajo_valss.update({"incidencia_id_holidays": created_holidays.id})
                resource_calendar = self.env['resource.calendar.leaves']
                resource_calendar_vals.update({'name': horas_de_trabajo_valss.get('incidencia'),
                                               'company_id': 1,
                                               'calendar_id': 4,
                                               'tz': 'America/Mexico_City',
                                               'holiday_id': created_holidays.id})
                resource_calendar.create(resource_calendar_vals)
                horas_de_trabajo_valss.update({
                    "operador": holidays_vals.get('employee_id'),
                })
            elif horas_de_trabajo_valss['incidencia'] == 'WORK_100':
                horas_de_trabajo_valss.update({                    
                    "day1_name": 4.75,
                    "day2_name": 4.75,
                    "day3_name": 0,
                    "day4_name": 0,
                })
        else:
            raise UserError(
                ('La Incidencia ha sido validada y no se puede modificar, comuniquese con el departamento de Recursos Humanos'))

        self.update(horas_de_trabajo_valss)



    @api.onchange('day1_name', 'day2_name', 'day3_name', 'day4_name')
    def aseee(self):
        incidencias_list=['FJS','FJC', 'FI', 'FR', 'VAC', 'INC_RT', 'INC_EG', 'INC_MAT']
        if self.incidencia in incidencias_list:
            horas_de_trabajo_vals = {}
            horas_de_trabajo_vals.update({
                "day1_name": 0,
                "day2_name": 0,
                "day3_name": 0,
                "day4_name": 0,
            })
            self.update(horas_de_trabajo_vals)
