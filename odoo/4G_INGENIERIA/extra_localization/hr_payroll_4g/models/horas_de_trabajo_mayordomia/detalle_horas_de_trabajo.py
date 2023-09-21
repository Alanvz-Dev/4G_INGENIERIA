# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class detalle_horas_de_trabajo(models.Model):
    _name = 'hr_payroll_4g.detalle_horas_de_trabajo'
    _rec_name = 'fecha'
    fecha = fields.Date()
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho'),
                              ('cancel', 'Cancelado')], string='Estado', default='draft')
    horas_de_trabajo_id = fields.One2many(
        'hr_payroll_4g.horas_de_trabajo', 'detalle_horas_de_trabajo_ids')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        creado =0
        hr_contract_obj = self.env['hr.contract']
        holydays_obj = self.env['hr.holidays']
        mayordomia_horas_de_trabajo = self.env['hr_payroll_4g.horas_de_trabajo']
        _detalle_horas_de_trabajo = super(detalle_horas_de_trabajo, self).create(vals)
        employee_ids = hr_contract_obj.search([('employee_id','!=',False),('state', 'in', ['open'])])
        for empleado in employee_ids:
            if empleado.employee_id.id==280:
                print('revisar')
            vals_horas_de_trabajo = {}
            vals_horas_de_trabajo.update({"operador": empleado.employee_id.id})
            id_holiday_existente = holydays_obj.get_exists_holiday(vals.get('fecha'), empleado.employee_id.id)
            if id_holiday_existente:
                if id_holiday_existente.holiday_status_id.name in ['FJS', 'FJC', 'FI', 'FR', 'VAC', 'INC_RT', 'INC_EG', 'INC_MAT']:
                    vals_horas_de_trabajo.update({
                        'incidencia': id_holiday_existente.holiday_status_id.name,
                        'departamento':empleado.employee_id.department_id.id,
                        'incidencia_id_holidays': id_holiday_existente.id,
                        'read_only': id_holiday_existente.state == 'validate' or False,
                        "day1_name": 0,
                        "day2_name": 0,
                        "day3_name": 0,
                        "day4_name": 0,
                        "detalle_horas_de_trabajo_ids": _detalle_horas_de_trabajo.id})
                    mayordomia_horas_de_trabajo.create(vals_horas_de_trabajo)
                    creado=creado+1
                    print('Creado Arriba_ '+str(creado) +'\t' + str(empleado.employee_id.id))
            else:
                mayordomia_horas_de_trabajo_vals_pago_completo = {
                    'departamento':empleado.employee_id.department_id.id,
            "operador": empleado.employee_id.id,
            "day1_name": 4.75,
            "day2_name": 4.75,
            'total_de_horas': 9.5,
            "detalle_horas_de_trabajo_ids": _detalle_horas_de_trabajo.id}
                mayordomia_horas_de_trabajo.create(mayordomia_horas_de_trabajo_vals_pago_completo)
                creado=creado+1
                print('Creado Abajo _ '+str(creado) +'\t' + str(empleado.employee_id.id))
        return _detalle_horas_de_trabajo



#Cehcar
    @api.one
    def unlink(self):
        horas_de_trabajo = self.env['hr_payroll_4g.horas_de_trabajo'].search([('detalle_horas_de_trabajo_ids', 'in', [self.id])])
        for item in horas_de_trabajo:
            if item.incidencia_id_holidays.id > 1:
                resource_calendar_leaves = self.env['resource.calendar.leaves'].search([('holiday_id', 'in', [item.incidencia_id_holidays.id])])
                self.env['hr.holidays'].search([('id', 'in', [item.incidencia_id_holidays.id])]).unlink()
                resource_calendar_leaves.unlink()
        horas_de_trabajo.unlink()
        return super(detalle_horas_de_trabajo, self).unlink()
