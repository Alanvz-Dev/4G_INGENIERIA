# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime

from ...scripts.sql_server import Get_Axtrax_Attendandce


class detalle_horas_de_trabajo_nomina(models.Model):
    _name = 'hr_payroll_4g.detalle_horas_de_trabajo_nomina'
    _rec_name = 'fecha'
    fecha = fields.Date()
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho'),
                              ('cancel', 'Cancelado')],
                             string='Estado', default='draft')
    horas_de_trabajo_id = fields.One2many(
        'hr_payroll_4g.horas_de_trabajo_nomina', 'horas_de_trabajo_nomina_ids')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        hr_contract_obj = self.env['hr.contract']
        holydays_obj = self.env['hr.holidays']
        hr_horas_de_trabajo_nomina = self.env['hr_payroll_4g.horas_de_trabajo_nomina']
        vals_horas_de_trabajo_nomina = {}
        vals_historial_de_tiempo = {}
        _detalle_horas_de_trabajo_nomina = super(
            detalle_horas_de_trabajo_nomina, self).create(vals)
        employee_ids = hr_contract_obj.search(
            [('employee_id', '>=', 1), ('state', '=', 'open')])
        for empleado in employee_ids:
            if empleado.employee_id.id == 257:
                print('err')

            vals_horas_de_trabajo_nomina = {}
            vals_horas_de_trabajo_nomina.update({"horas_de_trabajo_nomina_ids": _detalle_horas_de_trabajo_nomina.id,
                                                "operador": empleado.employee_id.id, 'departamento': empleado.employee_id.department_id.id, })
            id_holiday_existente = holydays_obj.get_exists_holiday(
                vals.get('fecha'), empleado.employee_id.id)



            vals_horas_de_trabajo_nomina.update(
                {'incidencia_id_holidays': id_holiday_existente.id or False})
            if id_holiday_existente.name == 'FI':
                vals_horas_de_trabajo_nomina.update(
                    {'bono_de_asistencia': False})
                vals_horas_de_trabajo_nomina.update(
                    {'bono_de_puntualidad': False})
            if id_holiday_existente.name in ['FJS', 'FJC', 'FR', 'VAC', 'INC_RT', 'INC_EG', 'INC_MAT']:
                vals_horas_de_trabajo_nomina.update(
                    {'bono_de_asistencia': True})
                vals_horas_de_trabajo_nomina.update(
                    {'bono_de_puntualidad': True})

            empleado_administrativo = self.env['hr_payroll_4g.empleados_administrativos'].search(
                [('empleado', 'in', [empleado.employee_id.id])])
            id_axtraxng = self.env['hr.employee'].browse(
                int(vals_horas_de_trabajo_nomina.get('operador')))
            horas_checador = []
            if id_axtraxng.id == 276:
                print('err')
            try:
                horas_checador = Get_Axtrax_Attendandce(
                    id_axtraxng.idaxtraxng, vals.get('fecha'))
            except:
                print(id_axtraxng)
            if empleado_administrativo and not id_holiday_existente:
                vals_horas_de_trabajo_nomina.update({"horas_mayordomia": 9.5,
                                                     "horas_checador": 10,
                                                     "valid": True,
                                                     "nota": "Administrativo",
                                                     "horas_a_pagar": (10),
                                                     'entrada_salida': '<p style="color:red;">'+'07:00'+'</p> <p style="color:blue;">'+'17:00'+'</p>',
                                                     "bono_de_puntualidad": True,
                                                     "bono_de_asistencia": True})
                hr_horas_de_trabajo_nomina.create(vals_horas_de_trabajo_nomina)
                continue
            elif not empleado_administrativo and id_holiday_existente:
                print(self.get_values_for_extisting_holiday(
                    id_holiday_existente, vals_horas_de_trabajo_nomina, horas_checador))
                hr_horas_de_trabajo_nomina.create(self.get_values_for_extisting_holiday(
                    id_holiday_existente, vals_horas_de_trabajo_nomina, horas_checador))
                continue
            detalle_dias_de_trabajo = self.env['hr_payroll_4g.detalle_horas_de_trabajo'].search(
                [('fecha', '=', vals.get('fecha'))]).ids
            if not detalle_dias_de_trabajo:
                raise UserError(
                    ("No esta creado el día de trabajo : "+vals.get('fecha')))
            contrato = self.env['hr.contract'].search([('employee_id', '!=', False), ('employee_id', 'in', [
                                                      int(vals_horas_de_trabajo_nomina.get('operador'))])])
            print(contrato)
            line_horas_de_trabajo = self.env['hr_payroll_4g.horas_de_trabajo'].search(
                [('operador', '=', contrato.employee_id.id), ('detalle_horas_de_trabajo_ids', '=', detalle_dias_de_trabajo[0])])
            horas_de_trabajo_mayordomia = 0
            try:
                horas_de_trabajo_mayordomia = line_horas_de_trabajo.day1_name+line_horas_de_trabajo.day2_name + \
                    line_horas_de_trabajo.day3_name+line_horas_de_trabajo.day4_name
            except:
                print('err')
            vals_balance_de_horas = []
            if line_horas_de_trabajo.fuera_de_planta:
                vals_balance_de_horas.append({
                    'balance_de_horas': 0,
                    'bono_de_asistencia': True,
                    'bono_de_puntualidad': True,
                    'departamento': contrato.employee_id.department_id.id,
                    'entrada_salida': '<p style="color:red;">07:00</p> <p style="color:blue;">17:00</p>',
                    'horas_a_pagar': 10,
                    'horas_checador': 10.0,
                    'horas_de_trabajo_nomina_ids': _detalle_horas_de_trabajo_nomina.id,
                    'horas_mayordomia': 9.5,
                    'incidencia_id_holidays': False,
                    'operador': contrato.employee_id.id,
                    'valid': True,
                    'nota': 'Trabajó fuera de planta'
                })
            else:
                vals_balance_de_horas = self.balance_de_horas(
                    horas_checador, horas_de_trabajo_mayordomia, id_holiday_existente, empleado, vals_horas_de_trabajo_nomina)
            print(vals_balance_de_horas)
            print(vals_balance_de_horas[0])
            created = self.env['hr_payroll_4g.horas_de_trabajo_nomina'].create(
                vals_balance_de_horas[0])
            print(created)

            if len(vals_balance_de_horas) > 1:
                vals_historial_de_tiempo.update({
                    'horas_de_trabajo_nomina_line': created.id
                })
                try:
                    self.env['hr_payroll_4g.historial_de_tiempo'].create(
                        vals_balance_de_horas[1])
                except:
                    pass

        return _detalle_horas_de_trabajo_nomina

    def get_values_for_extisting_holiday(self, existing_holyday, vals, horas_checador):
        strx = ""
        if horas_checador[2] > 1:
            strx = "Tiene Horas registradas en el checador"

        if existing_holyday.holiday_status_id.name in ['FJS', 'FJC', 'FR', 'VAC', 'INC_RT', 'INC_EG', 'INC_MAT']:
            vals.update({"horas_mayordomia": 0,
                         "horas_checador": horas_checador[2],
                         "valid": True,
                         "horas_a_pagar": (0),
                         "incidencia_id_holidays": existing_holyday.id or False,
                         "nota": "Estado de incidencia "+existing_holyday.state+'\n'+strx,
                         'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                         "bono_de_puntualidad": True,
                         "bono_de_asistencia": True})
        elif existing_holyday.holiday_status_id.name in ['FI']:
            vals.update({"horas_mayordomia": 0,
                         "horas_checador": horas_checador[2],
                         "valid": True,
                         "horas_a_pagar": (0),
                         "nota": "Estado de incidencia "+existing_holyday.state+'\n'+strx,
                         "incidencia_id_holidays": existing_holyday.id or False,
                         'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                         "bono_de_puntualidad": False,
                         "bono_de_asistencia": False})
        return vals

    def balance_de_horas(self, horas_checador, horas_de_trabajo_mayordomia, holiday, id_empleado, vals_horas_de_trabajo_nomina):

        strx = ""
        if horas_checador[2] > 1:
            strx = "Tiene Horas registradas en el checador"
        vals_historial_de_tiempo = {}
        if horas_checador[2] >= 11 and horas_de_trabajo_mayordomia >= 10:
            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            vals_historial_de_tiempo.update({
                'operador': id_empleado,
                'active': True,
                'horas_a_favor': (horas_checador[2]-10),
                'state': 'to_approve',
                'tipo_pago': 'undef',
            })
            vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                 "horas_checador": horas_checador[2],
                                                 "valid": True,
                                                 "nota": "Estado de incidencia "+str(holiday.state)+'\n'+strx,
                                                 "incidencia_id_holidays": holiday.id or False,
                                                 "balance_de_horas": (horas_checador[2]-10),
                                                 "horas_a_pagar": (10),
                                                 'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                 "bono_de_puntualidad": True,
                                                 "bono_de_asistencia": True
                                                 })
        elif horas_checador[2] < 10 and horas_de_trabajo_mayordomia > 10:
            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            if holiday.state:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Revisión Recomendada, las horas de Mayordomía\necxeden las 9.5 Hrs.+\n Estado de incidencia "+holiday.state+"\n"})
            else:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Revisión Recomendada, las horas de Mayordomía\necxeden las 9.5 Hrs."+"\n"})

            vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                 "horas_checador": horas_checador[2],
                                                 "valid": False,
                                                 "incidencia_id_holidays": holiday.id or False,
                                                 "balance_de_horas": (10-horas_checador[2]),
                                                 "horas_a_pagar": (10),
                                                 'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                 "bono_de_asistencia": True,
                                                 "bono_de_puntualidad": True,
                                                 })

        elif horas_checador[2] > 10 and horas_de_trabajo_mayordomia < 9.5:

            if holiday.state:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Revisión Recomendada, las horas del Checador\necxeden las 10 Hrs.+\n Estado de incidencia "+holiday.state+"\n"})
            else:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Revisión Recomendada'+'las horas del Checador\necxeden las 10 Hrs."+"\n"})
            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                 "horas_checador": horas_checador[2],
                                                 "valid": False,
                                                 "incidencia_id_holidays": holiday.id or False,
                                                 "balance_de_horas": (10-horas_checador[2]),
                                                 "horas_a_pagar": (10),
                                                 'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                 "bono_de_asistencia": True,
                                                 "bono_de_puntualidad": True,
                                                 })

        elif horas_checador[2] == 10 and horas_de_trabajo_mayordomia == 9.5:
            if holiday.state:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Estado de incidencia "+holiday.state+'\n'+strx})
            else:
                vals_horas_de_trabajo_nomina.update({"Ok"})

            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                 "horas_checador": horas_checador[2],
                                                 "valid": True,
                                                 "incidencia_id_holidays": holiday.id or False,
                                                 "balance_de_horas": 0,
                                                 "horas_a_pagar": (10),
                                                 'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                 "bono_de_puntualidad": True,
                                                 "bono_de_asistencia": True
                                                 })

        elif horas_checador[2] > 8 and horas_checador[2] < 10 and horas_de_trabajo_mayordomia > 8 and horas_de_trabajo_mayordomia < 9.5:
            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            try:

                vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                     "horas_checador": horas_checador[2],
                                                     "valid": False,
                                                     "nota": "Revisión Recomendada, la ausencia de este empleado es de entre 1.5 y 2 horas.+\n Estado de incidencia "+holiday.state or 'Revisión Recomendada, la ausencia de este empleado es de entre 1.5 y 2 horas'+"\n",
                                                     "incidencia_id_holidays": holiday.id or False,
                                                     "balance_de_horas": 0,
                                                     "horas_a_pagar": horas_checador[2],
                                                     'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                     "bono_de_asistencia": True,
                                                     "bono_de_puntualidad": True,
                                                     })

            except:
                vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                     "horas_checador": horas_checador[2],
                                                     "valid": False,
                                                     "nota": "Revisión Recomendada\n",
                                                     "incidencia_id_holidays": holiday.id or False,
                                                     "balance_de_horas": 0,
                                                     "horas_a_pagar": horas_checador[2],
                                                     'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                     "bono_de_asistencia": True,
                                                     "bono_de_puntualidad": True,
                                                     })

        elif horas_checador[2] > 6 and horas_checador[2] < 8 and horas_de_trabajo_mayordomia > 6 and horas_de_trabajo_mayordomia < 8:

            if holiday.state:
                vals_horas_de_trabajo_nomina.update(
                    {"Revisión Recomendada, la ausencia de este empleado es de entre 2.5 y 4 horas.+\n Estado de incidencia "+holiday.state+"\n"})
            else:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Revisión Recomendada, la ausencia de este empleado es de entre 1.5 y 2 horas"+"\n"})
            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            x = holiday.state or ''
            vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                 "horas_checador": horas_checador[2],
                                                 "valid": False,
                                                 "nota": "Revisión Recomendada, la ausencia de este empleado es de entre 2.5 y 4 horas. Estado de incidencia "+x+"\n",
                                                 "incidencia_id_holidays": holiday.id or False,
                                                 "balance_de_horas": 0,
                                                 "horas_a_pagar": horas_checador[2],
                                                 'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                 "bono_de_asistencia": True
                                                 })
        elif horas_checador[2] >= 9 and horas_checador[2] < 10 and horas_de_trabajo_mayordomia >= 9 and horas_de_trabajo_mayordomia <= 10:
            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                 "horas_checador": horas_checador[2],
                                                 "valid": False,
                                                 "nota": "Revisión Recomendada, la ausencia de este empleado es de entre .2 y 1 hora \n",
                                                 "incidencia_id_holidays": holiday.id or False,
                                                 "balance_de_horas": 0,
                                                 "horas_a_pagar": horas_checador[2],
                                                 'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>',
                                                 "bono_de_asistencia": True,
                                                 "bono_de_puntualidad": False,
                                                 })

        else:
            if holiday.state:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Error de Revisión estado de incidencia "+holiday.state+"\n"})
            else:
                vals_horas_de_trabajo_nomina.update(
                    {"nota": "Error de Revisión, por favor revise manualmente"+"\n"})

            # Se insertan las horas extra para validacion y se le insertan sus 9.horas para pago
            vals_horas_de_trabajo_nomina.update({"horas_mayordomia": horas_de_trabajo_mayordomia,
                                                 "horas_checador": horas_checador[2],
                                                 "valid": False,
                                                 "incidencia_id_holidays": holiday.id or False,
                                                 "balance_de_horas": 0,
                                                 "horas_a_pagar": horas_checador[2],
                                                 'entrada_salida': '<p style="color:red;">'+horas_checador[0]+'</p> <p style="color:blue;">'+horas_checador[1]+'</p>'
                                                 })
        return [vals_horas_de_trabajo_nomina, vals_historial_de_tiempo]
