import time
from datetime import time as datetime_time,datetime
from dateutil import relativedelta
import ast
import babel
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from collections import OrderedDict, defaultdict
from datetime import datetime,timedelta
class Payslip(models.Model):
    _inherit = 'hr.payslip'

    # YTI TODO To rename. This method is not really an onchange, as it is not in any view
    # employee_id and contract_id could be browse records
    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False, resumen_nomina_id=False):
        #defaults
        res = {
            'value': {
                'line_ids': [],
                #delete old input lines
                'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
                #delete old worked days lines
                'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
                #'details_by_salary_head':[], TODO put me back
                'name': '',
                'contract_id': False,
                'struct_id': False,
            }
        }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee = self.env['hr.employee'].browse(employee_id)
        locale = self.env.context.get('lang') or 'en_US'
        res['value'].update({
            'name': _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))),
            'company_id': employee.company_id.id,
        })

        if not self.env.context.get('contract'):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(employee, date_from, date_to)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(employee, date_from, date_to)

        if not contract_ids:
            return res
        contract = self.env['hr.contract'].browse(contract_ids[0])
        res['value'].update({
            'contract_id': contract.id
        })
        struct = contract.struct_id
        if not struct:
            return res
        res['value'].update({
            'struct_id': struct.id,
        })
        #computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        
        if resumen_nomina_id:
            resumen_nomina_line = self.env['hr_payroll_pr.resumen_nomina_line'].search([('resumen_nomina_id','in',[resumen_nomina_id]),('operador','in',[employee.id])])
            print(resumen_nomina_line)                 
            worked_days_line_ids = self.get_worked_day_lines_mod_4g(contracts, date_from, date_to,((resumen_nomina_line.total_de_horas)*7)/50,resumen_nomina_line.total_de_horas)
            resumen_nomina_line.worked_day=worked_days_line_ids            
            
        else:        
            worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)        


        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        res['value'].update({
            'worked_days_line_ids': worked_days_line_ids,
            'input_line_ids': input_line_ids,
        })
        return res

    @api.model
    def get_worked_day_lines_mod_4g(self, contracts, date_from, date_to,work100=False,horas_p=False):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        horas_obj = self.env['horas.nomina']
        tipo_de_hora_mapping = {'1': 'HEX1', '2': 'HEX2', '3': 'HEX3'}

        def is_number(s):
            try:
                return float(s)
            except ValueError:
                return 0

        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(
                fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.combine(
                fields.Date.from_string(date_to), datetime_time.max)
            nb_of_days = (day_to - day_from).days + 1

            # compute Prima vacacional en fecha correcta
            if contract.tipo_prima_vacacional == '01':
                date_start = contract.date_start
                if date_start:
                    d_from = fields.Date.from_string(date_from)
                    d_to = fields.Date.from_string(date_to)

                    date_start = fields.Date.from_string(date_start)
                    if datetime.today().year > date_start.year:
                        d_from = d_from.replace(date_start.year)
                        if str(d_to.day) == '29' and str(d_to.month) == '2':
                            d_to -= timedelta(days=1)
                        d_to = d_to.replace(date_start.year)

                        if d_from <= date_start <= d_to:
                            diff_date = day_to - \
                                datetime.strptime(
                                    contract.date_start, "%Y-%m-%d")
                            years = diff_date.days / 365.0
                            antiguedad_anos = int(years)
                            tabla_antiguedades = contract.tablas_cfdi_id.tabla_antiguedades.filtered(
                                lambda x: x.antiguedad <= antiguedad_anos)
                            tabla_antiguedades = tabla_antiguedades.sorted(
                                lambda x: x.antiguedad, reverse=True)
                            vacaciones = tabla_antiguedades and tabla_antiguedades[0].vacaciones or 0
                            prima_vac = tabla_antiguedades and tabla_antiguedades[0].prima_vac or 0
                            attendances = {
                                'name': 'Prima vacacional',
                                'sequence': 2,
                                'code': 'PVC',
                                # work_data['days'],
                                'number_of_days': vacaciones * prima_vac / 100.0,
                                # 'number_of_hours': 1['hours'],
                                'contract_id': contract.id,
                            }
                            res.append(attendances)

            # compute Prima vacacional
            if contract.tipo_prima_vacacional == '03':
                date_start = contract.date_start
                if date_start:
                    d_from = fields.Date.from_string(date_from)
                    d_to = fields.Date.from_string(date_to)

                    date_start = fields.Date.from_string(date_start)
                    if datetime.today().year > date_start.year and d_from.day > 15:
                        d_from = d_from.replace(date_start.year)
                        d_from = d_from.replace(day=1)
                        if str(d_to.day) == '29' and str(d_to.month) == '2':
                            d_to -= timedelta(days=1)
                        d_to = d_to.replace(date_start.year)

                        if d_from <= date_start <= d_to:
                            diff_date = day_to - \
                                datetime.strptime(
                                    contract.date_start, "%Y-%m-%d")
                            years = diff_date.days / 365.0
                            antiguedad_anos = int(years)
                            tabla_antiguedades = contract.tablas_cfdi_id.tabla_antiguedades.filtered(
                                lambda x: x.antiguedad <= antiguedad_anos)
                            tabla_antiguedades = tabla_antiguedades.sorted(
                                lambda x: x.antiguedad, reverse=True)
                            vacaciones = tabla_antiguedades and tabla_antiguedades[0].vacaciones or 0
                            prima_vac = tabla_antiguedades and tabla_antiguedades[0].prima_vac or 0
                            attendances = {
                                'name': 'Prima vacacional',
                                'sequence': 2,
                                'code': 'PVC',
                                # work_data['days'],
                                'number_of_days': vacaciones * prima_vac / 100.0,
                                # 'number_of_hours': 1['hours'],
                                'contract_id': contract.id,
                            }
                            res.append(attendances)

            # compute Prima dominical
            if contract.prima_dominical:
                domingos = 0
                d_from = fields.Date.from_string(date_from)
                d_to = fields.Date.from_string(date_to)
                for i in range((d_to - d_from).days + 1):
                    if (d_from + timedelta(days=i+1)).weekday() == 0:
                        domingos = domingos + 1
                attendances = {
                    'name': 'Prima dominical',
                            'sequence': 2,
                            'code': 'PDM',
                            'number_of_days': domingos,  # work_data['days'],
                            #'number_of_hours': 1['hours'],
                            'contract_id': contract.id,
                }
                res.append(attendances)

            # compute leave days
            leaves = {}
            leave_days = 0
            
            print(leave_days)
       
            
            
            factor = 0
            if contract.semana_inglesa:
                factor = 7.0/5.0
            else:
                factor = 7.0/6.0

            if contract.periodicidad_pago == '04':
                dias_pagar = 15
            if contract.periodicidad_pago == '02':
                dias_pagar = 7

            #Itera las faltas desde hasta
            day_leave_intervals = contract.employee_id.iter_leaves(
                day_from, day_to, calendar=contract.resource_calendar_id)
            #Por cada dia del intervalo
            for day_intervals in day_leave_intervals:
                for interval in day_intervals:
                    #Busca registro con  el id del resource calendar
                    holiday = interval[2]['leaves'].holiday_id
                    if holiday.state=='validate':

                        #Obtiene el holiday_id
                        current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                            'name': holiday.holiday_status_id.name or _('Global Leaves'),
                            'sequence': 5,
                            'code': holiday.holiday_status_id.name or 'GLOBAL',
                            'number_of_days': 0.0,
                            'number_of_hours': 0.0,
                            'contract_id': contract.id,
                        })
                        ###########Lo vuelve a insetrar
                        #resta la fecha inicial - la fecha final
                        leave_time = (interval[1] - interval[0]).seconds / 3600
                        print(leave_time)
                        #current_leave_struct['number_of_hours'] += leave_time
                        work_hours = contract.employee_id.get_day_work_hours_count(
                            interval[0].date(), calendar=contract.resource_calendar_id)
                        if work_hours and contract.septimo_dia:
                            if contract.incapa_sept_dia:
                                if (holiday.holiday_status_id.name == 'FJS' or holiday.holiday_status_id.name == 'FI' or holiday.holiday_status_id.name == 'FR' or holiday.holiday_status_id.name == 'INC_EG' or holiday.holiday_status_id.name == 'INC_RT' or holiday.holiday_status_id.name == 'INC_MAT') and holiday.state == 'validate':

                                    leave_days += (leave_time / work_hours)*factor



                                    current_leave_struct['number_of_days'] += (
                                        leave_time / work_hours)*factor


                                    if leave_days > dias_pagar:



                                        leave_days = dias_pagar

                                    if current_leave_struct['number_of_days'] > dias_pagar:
                                        current_leave_struct['number_of_days'] = dias_pagar
                                else:
                                    ##Despues de iterar si el holiday es diferente a alguno de estos 
                                    if holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3':
                                        #entonces suma la incidencia que ya tiene +1
                                        leave_days += leave_time / work_hours


                                    ##Si no se encuentra el holiday arriba    
                                    current_leave_struct['number_of_days'] += leave_time / work_hours
                            else:
                                #Si el holiday es igual a cualquira de estos
                                if  (holiday.holiday_status_id.name == 'FJC' or holiday.holiday_status_id.name == 'FJS' or holiday.holiday_status_id.name == 'FI' or holiday.holiday_status_id.name == 'FR') and holiday.state == 'validate':
                                    leave_days += (leave_time / work_hours)*factor
                                    #el leave day será 1.4



                                    current_leave_struct['number_of_days'] += (
                                        leave_time / work_hours)*factor
                                    #si la cantidad de faltas es mayor a los dias a pagar
                                    # la cantidad de dias sera igual a la cantidad a pagar    
                                    if leave_days > dias_pagar:




                                        leave_days = dias_pagar


                                    if current_leave_struct['number_of_days'] > dias_pagar:
                                        current_leave_struct['number_of_days'] = dias_pagar
                                else:
                                    if (holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3') and holiday.state == 'validate':
                                        leave_days += leave_time / work_hours*factor
                                        print(leave_days)
                                        #1
                                        #2
                                    ##Como vacaciones no cae en ninguno de los rubros de arriba entonces se calcula * 1.4
                                    current_leave_struct['number_of_days'] += ((leave_time / work_hours)*1.4)
                        elif work_hours:
                            ############
                            if contract.incapa_sept_dia:

                                if (holiday.holiday_status_id.name == 'INC_EG' or holiday.holiday_status_id.name == 'INC_RT' or holiday.holiday_status_id.name == 'INC_MAT') and holiday.state == 'validate':
                                    print(factor)
                                    print(work_hours)


                                    print(current_leave_struct['number_of_days'])
                                    leave_days += (leave_time / work_hours)*factor



                                    current_leave_struct['number_of_days'] += (
                                        leave_time / work_hours)*factor
                                else:
                                    if (holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3') and holiday.state == 'validate':

                                        leave_days += leave_time / work_hours



                                    current_leave_struct['number_of_days'] += leave_time / work_hours


                            else:
                                if (holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3'):
                                    print(factor)
                                    print(work_hours)
                                    print(leave_days)
                                    print(current_leave_struct['number_of_days'])
                                    leave_days += leave_time / work_hours
                                    print(leave_days)
                                    



                                current_leave_struct['number_of_days'] += leave_time / work_hours

            # compute worked days
            work_data = contract.employee_id.with_context(no_tz_convert=True).get_work_days_data(
                day_from, day_to, calendar=contract.resource_calendar_id)
            print(work_data)
            number_of_days = 0

            # ajuste en caso de nuevo ingreso
            nvo_ingreso = False
            date_start_1 = contract.date_start
            date_start_1 = datetime.strptime(date_start_1, "%Y-%m-%d")
            d_from_1 = datetime.strptime(date_from, "%Y-%m-%d")
            d_to_1 = datetime.strptime(date_to, "%Y-%m-%d")
            if date_start_1 > d_from_1:
                work_data['days'] = (d_to_1 - date_start_1).days + 1
                nvo_ingreso = True

            #dias_a_pagar = contract.dias_pagar
            _logger.info('dias trabajados %s  dias incidencia %s',
                         work_data['days'], leave_days)

            if work_data['days'] < 100:
                # periodo para nómina quincenal
                if contract.periodicidad_pago == '04':
                    if contract.tipo_pago == '01' and nb_of_days < 30:
                        total_days = work_data['days'] + leave_days
                        if total_days != 15:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 15
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = 15 - leave_days
                        else:
                            number_of_days = work_data['days']
                        if contract.sept_dia:
                            aux = 2.5
                            number_of_days -= aux
                            attendances = {
                                'name': _("Séptimo día"),
                                'sequence': 3,
                                'code': "SEPT",
                                'number_of_days': aux,
                                'number_of_hours': 0.0,
                                'contract_id': contract.id,
                            }
                            res.append(attendances)
                    elif contract.tipo_pago == '03' and nb_of_days < 30:
                        total_days = work_data['days'] + leave_days
                        if total_days != 15.21:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 15.21
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] * \
                                    15.21 / 15 - leave_days
                            else:
                                number_of_days = 15.21 - leave_days
                        else:
                            number_of_days = work_data['days'] * 15.21 / 15
                        if contract.sept_dia:
                            aux = 2.21
                            number_of_days -= aux
                            attendances = {
                                'name': _("Séptimo día"),
                                'sequence': 3,
                                'code': "SEPT",
                                'number_of_days': aux,
                                'number_of_hours': 0.0,
                                'contract_id': contract.id,
                            }
                            res.append(attendances)
                    else:
                        dias_periodo = (datetime.strptime(
                            date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days + 1
                        total_days = work_data['days'] + leave_days
                        if total_days != dias_periodo:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = dias_periodo
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = dias_periodo - leave_days
                        else:
                            number_of_days = work_data['days']
                # calculo para nóminas semanales
                elif contract.periodicidad_pago == '02' and nb_of_days < 30:
                    number_of_days = work_data['days']
                    if contract.septimo_dia:  # falta proporcional por septimo día
                        total_days = work_data['days'] + leave_days
                        if total_days != 7:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 7
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = 7 - leave_days
                        else:
                            number_of_days = work_data['days']
                    if contract.sept_dia:  # septimo día
                        if number_of_days == 0:
                            if leave_days != 7:

                                number_of_days = work_data['days']
                        if contract.semana_inglesa:
                            aux = number_of_days / 7 * 2
                        else:
                            aux = number_of_days - int(number_of_days)
                        _logger.info('number_of_days %s  aux %s',
                                     number_of_days, aux)
                        if aux > 0:
                            number_of_days -= aux
                        elif number_of_days > 0:
                            if contract.semana_inglesa:
                                aux = 2
                            else:
                                aux = 1
                            number_of_days -= aux
                        attendances = {
                            'name': _("Séptimo día"),
                            'sequence': 3,
                            'code': "SEPT",
                            'number_of_days': aux,
                            'number_of_hours': 0.0,
                            'contract_id': contract.id,
                        }
                        res.append(attendances)
                # calculo para nóminas mensuales
                elif contract.periodicidad_pago == '05':
                    if contract.tipo_pago == '01':
                        total_days = work_data['days'] + leave_days
                        if total_days != 30:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 30
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = 30 - leave_days
                    elif contract.tipo_pago == '03':
                        total_days = work_data['days'] + leave_days
                        if total_days != 30.42:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 30.42
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] * \
                                    30.42 / 30 - leave_days
                            else:
                                number_of_days = 30.42 - leave_days
                        else:
                            number_of_days = work_data['days'] * 30.42 / 30
                    else:
                        dias_periodo = (datetime.strptime(
                            date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days + 1
                        total_days = work_data['days'] + leave_days
                        if total_days != dias_periodo:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = dias_periodo
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = dias_periodo - leave_days
                        else:
                            number_of_days = work_data['days']
                else:
                    number_of_days = work_data['days']
            else:
                date_start = contract.date_start
                date_start = datetime.strptime(date_start, "%Y-%m-%d")
                d_from = datetime.strptime(date_from, "%Y-%m-%d")
                d_to = datetime.strptime(date_to, "%Y-%m-%d")
                if date_start > d_from:
                    number_of_days = (d_to - date_start).days + 1 - leave_days
                else:
                    number_of_days = (d_to - d_from).days + 1 - leave_days
            attendances = {
                'name': _("Días de trabajo"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work100 ,  # or number_of_days  work_data['days'],
                'number_of_hours': horas_p,
                'contract_id': contract.id,
            }

            res.append(attendances)

            # Compute horas extas
            horas = horas_obj.search([('employee_id', '=', contract.employee_id.id), (
                'fecha', '>=', date_from), ('fecha', '<=', date_to), ('state', '=', 'done')])
            horas_by_tipo_de_horaextra = defaultdict(list)
            for h in horas:
                horas_by_tipo_de_horaextra[h.tipo_de_hora].append(h.horas)

            for tipo_de_hora, horas_set in horas_by_tipo_de_horaextra.items():
                work_code = tipo_de_hora_mapping.get(tipo_de_hora, '')
                number_of_days = len(horas_set)
                number_of_hours = sum(is_number(hs) for hs in horas_set)

                attendances = {
                    'name': _("Horas extras"),
                    'sequence': 2,
                    'code': work_code,
                    'number_of_days': number_of_days,
                    'number_of_hours': number_of_hours,
                    'contract_id': contract.id,
                }
                res.append(attendances)

            res.extend(leaves.values())

        return res


    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        horas_obj = self.env['horas.nomina']
        tipo_de_hora_mapping = {'1': 'HEX1', '2': 'HEX2', '3': 'HEX3'}

        def is_number(s):
            try:
                return float(s)
            except ValueError:
                return 0

        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(
                fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.combine(
                fields.Date.from_string(date_to), datetime_time.max)
            nb_of_days = (day_to - day_from).days + 1

            # compute Prima vacacional en fecha correcta
            if contract.tipo_prima_vacacional == '01':
                date_start = contract.date_start
                if date_start:
                    d_from = fields.Date.from_string(date_from)
                    d_to = fields.Date.from_string(date_to)

                    date_start = fields.Date.from_string(date_start)
                    if datetime.today().year > date_start.year:
                        d_from = d_from.replace(date_start.year)
                        if str(d_to.day) == '29' and str(d_to.month) == '2':
                            d_to -= timedelta(days=1)
                        d_to = d_to.replace(date_start.year)

                        if d_from <= date_start <= d_to:
                            diff_date = day_to - \
                                datetime.strptime(
                                    contract.date_start, "%Y-%m-%d")
                            years = diff_date.days / 365.0
                            antiguedad_anos = int(years)
                            tabla_antiguedades = contract.tablas_cfdi_id.tabla_antiguedades.filtered(
                                lambda x: x.antiguedad <= antiguedad_anos)
                            tabla_antiguedades = tabla_antiguedades.sorted(
                                lambda x: x.antiguedad, reverse=True)
                            vacaciones = tabla_antiguedades and tabla_antiguedades[0].vacaciones or 0
                            prima_vac = tabla_antiguedades and tabla_antiguedades[0].prima_vac or 0
                            attendances = {
                                'name': 'Prima vacacional',
                                'sequence': 2,
                                'code': 'PVC',
                                # work_data['days'],
                                'number_of_days': vacaciones * prima_vac / 100.0,
                                # 'number_of_hours': 1['hours'],
                                'contract_id': contract.id,
                            }
                            res.append(attendances)

            # compute Prima vacacional
            if contract.tipo_prima_vacacional == '03':
                date_start = contract.date_start
                if date_start:
                    d_from = fields.Date.from_string(date_from)
                    d_to = fields.Date.from_string(date_to)

                    date_start = fields.Date.from_string(date_start)
                    if datetime.today().year > date_start.year and d_from.day > 15:
                        d_from = d_from.replace(date_start.year)
                        d_from = d_from.replace(day=1)
                        if str(d_to.day) == '29' and str(d_to.month) == '2':
                            d_to -= timedelta(days=1)
                        d_to = d_to.replace(date_start.year)

                        if d_from <= date_start <= d_to:
                            diff_date = day_to - \
                                datetime.strptime(
                                    contract.date_start, "%Y-%m-%d")
                            years = diff_date.days / 365.0
                            antiguedad_anos = int(years)
                            tabla_antiguedades = contract.tablas_cfdi_id.tabla_antiguedades.filtered(
                                lambda x: x.antiguedad <= antiguedad_anos)
                            tabla_antiguedades = tabla_antiguedades.sorted(
                                lambda x: x.antiguedad, reverse=True)
                            vacaciones = tabla_antiguedades and tabla_antiguedades[0].vacaciones or 0
                            prima_vac = tabla_antiguedades and tabla_antiguedades[0].prima_vac or 0
                            attendances = {
                                'name': 'Prima vacacional',
                                'sequence': 2,
                                'code': 'PVC',
                                # work_data['days'],
                                'number_of_days': vacaciones * prima_vac / 100.0,
                                # 'number_of_hours': 1['hours'],
                                'contract_id': contract.id,
                            }
                            res.append(attendances)

            # compute Prima dominical
            if contract.prima_dominical:
                
                domingos = 0
                d_from = fields.Date.from_string(date_from)
                d_to = fields.Date.from_string(date_to)
                for i in range((d_to - d_from).days + 1):
                    if (d_from + timedelta(days=i+1)).weekday() == 0:
                        domingos = domingos + 1
                attendances = {
                    'name': 'Prima dominical',
                            'sequence': 2,
                            'code': 'PDM',
                            'number_of_days': domingos,  # work_data['days'],
                            #'number_of_hours': 1['hours'],
                            'contract_id': contract.id,
                }
                res.append(attendances)

            # compute leave days
            leaves = {}
            leave_days = 0
            
            print(leave_days)
       
            
            
            factor = 0
            if contract.semana_inglesa:
                factor = 7.0/5.0
            else:
                factor = 7.0/6.0

            if contract.periodicidad_pago == '04':
                dias_pagar = 15
            if contract.periodicidad_pago == '02':
                dias_pagar = 7

            #Itera las faltas desde hasta
            day_leave_intervals = contract.employee_id.iter_leaves(
                day_from, day_to, calendar=contract.resource_calendar_id)
            #Por cada dia del intervalo
            for day_intervals in day_leave_intervals:
                for interval in day_intervals:
                    #Busca registro con  el id del resource calendar
                    holiday = interval[2]['leaves'].holiday_id
                    if holiday.state=='validate':

                        #Obtiene el holiday_id
                        current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                            'name': holiday.holiday_status_id.name or _('Global Leaves'),
                            'sequence': 5,
                            'code': holiday.holiday_status_id.name or 'GLOBAL',
                            'number_of_days': 0.0,
                            'number_of_hours': 0.0,
                            'contract_id': contract.id,
                        })
                        ###########Lo vuelve a insetrar
                        #resta la fecha inicial - la fecha final
                        leave_time = (interval[1] - interval[0]).seconds / 3600
                        print(leave_time)
                        #current_leave_struct['number_of_hours'] += leave_time
                        work_hours = contract.employee_id.get_day_work_hours_count(
                            interval[0].date(), calendar=contract.resource_calendar_id)
                        if work_hours and contract.septimo_dia:
                            if contract.incapa_sept_dia:
                                if (holiday.holiday_status_id.name == 'FJS' or holiday.holiday_status_id.name == 'FI' or holiday.holiday_status_id.name == 'FR' or holiday.holiday_status_id.name == 'INC_EG' or holiday.holiday_status_id.name == 'INC_RT' or holiday.holiday_status_id.name == 'INC_MAT') and holiday.state == 'validate':

                                    leave_days += (leave_time / work_hours)*factor



                                    current_leave_struct['number_of_days'] += (
                                        leave_time / swork_hours)*factor


                                    if leave_days > dias_pagar:



                                        leave_days = dias_pagar

                                    if current_leave_struct['number_of_days'] > dias_pagar:
                                        current_leave_struct['number_of_days'] = dias_pagar
                                else:
                                    ##Despues de iterar si el holiday es diferente a alguno de estos 
                                    if holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3':
                                        #entonces suma la incidencia que ya tiene +1
                                        leave_days += leave_time / work_hours


                                    ##Si no se encuentra el holiday arriba    
                                    current_leave_struct['number_of_days'] += leave_time / work_hours
                            else:
                                #Si el holiday es igual a cualquira de estos
                                if  (holiday.holiday_status_id.name == 'FJC' or holiday.holiday_status_id.name == 'FJS' or holiday.holiday_status_id.name == 'FI' or holiday.holiday_status_id.name == 'FR') and holiday.state == 'validate':
                                    leave_days += (leave_time / work_hours)*factor
                                    #el leave day será 1.4



                                    current_leave_struct['number_of_days'] += (
                                        leave_time / work_hours)*factor
                                    #si la cantidad de faltas es mayor a los dias a pagar
                                    # la cantidad de dias sera igual a la cantidad a pagar    
                                    if leave_days > dias_pagar:




                                        leave_days = dias_pagar


                                    if current_leave_struct['number_of_days'] > dias_pagar:
                                        current_leave_struct['number_of_days'] = dias_pagar
                                else:
                                    if (holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3') and holiday.state == 'validate':
                                        leave_days += leave_time / work_hours*factor
                                        print(leave_days)
                                        #1
                                        #2
                                    ##Como vacaciones no cae en ninguno de los rubros de arriba entonces se calcula * 1.4
                                    current_leave_struct['number_of_days'] += ((leave_time / work_hours)*1.4)
                        elif work_hours:
                            ############
                            if contract.incapa_sept_dia:

                                if (holiday.holiday_status_id.name == 'INC_EG' or holiday.holiday_status_id.name == 'INC_RT' or holiday.holiday_status_id.name == 'INC_MAT') and holiday.state == 'validate':
                                    print(factor)
                                    print(work_hours)


                                    print(current_leave_struct['number_of_days'])
                                    leave_days += (leave_time / work_hours)*factor



                                    current_leave_struct['number_of_days'] += (
                                        leave_time / work_hours)*factor
                                else:
                                    if (holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3') and holiday.state == 'validate':

                                        leave_days += leave_time / work_hours



                                    current_leave_struct['number_of_days'] += leave_time / work_hours


                            else:
                                if (holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3'):
                                    print(factor)
                                    print(work_hours)
                                    print(leave_days)
                                    print(current_leave_struct['number_of_days'])
                                    leave_days += leave_time / work_hours
                                    print(leave_days)
                                    



                                current_leave_struct['number_of_days'] += leave_time / work_hours

            # compute worked days
            work_data = contract.employee_id.with_context(no_tz_convert=True).get_work_days_data(
                day_from, day_to, calendar=contract.resource_calendar_id)
            print(work_data)
            number_of_days = 0

            # ajuste en caso de nuevo ingreso
            nvo_ingreso = False
            date_start_1 = contract.date_start
            date_start_1 = datetime.strptime(date_start_1, "%Y-%m-%d")
            d_from_1 = datetime.strptime(date_from, "%Y-%m-%d")
            d_to_1 = datetime.strptime(date_to, "%Y-%m-%d")
            if date_start_1 > d_from_1:
                work_data['days'] = (d_to_1 - date_start_1).days + 1
                nvo_ingreso = True

            #dias_a_pagar = contract.dias_pagar
            _logger.info('dias trabajados %s  dias incidencia %s',
                         work_data['days'], leave_days)

            if work_data['days'] < 100:
                # periodo para nómina quincenal
                if contract.periodicidad_pago == '04':
                    if contract.tipo_pago == '01' and nb_of_days < 30:
                        total_days = work_data['days'] + leave_days
                        if total_days != 15:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 15
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = 15 - leave_days
                        else:
                            number_of_days = work_data['days']
                        if contract.sept_dia:
                            aux = 2.5
                            number_of_days -= aux
                            attendances = {
                                'name': _("Séptimo día"),
                                'sequence': 3,
                                'code': "SEPT",
                                'number_of_days': aux,
                                'number_of_hours': 0.0,
                                'contract_id': contract.id,
                            }
                            res.append(attendances)
                    elif contract.tipo_pago == '03' and nb_of_days < 30:
                        total_days = work_data['days'] + leave_days
                        if total_days != 15.21:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 15.21
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] * \
                                    15.21 / 15 - leave_days
                            else:
                                number_of_days = 15.21 - leave_days
                        else:
                            number_of_days = work_data['days'] * 15.21 / 15
                        if contract.sept_dia:
                            aux = 2.21
                            number_of_days -= aux
                            attendances = {
                                'name': _("Séptimo día"),
                                'sequence': 3,
                                'code': "SEPT",
                                'number_of_days': aux,
                                'number_of_hours': 0.0,
                                'contract_id': contract.id,
                            }
                            res.append(attendances)
                    else:
                        dias_periodo = (datetime.strptime(
                            date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days + 1
                        total_days = work_data['days'] + leave_days
                        if total_days != dias_periodo:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = dias_periodo
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = dias_periodo - leave_days
                        else:
                            number_of_days = work_data['days']
                # calculo para nóminas semanales
                elif contract.periodicidad_pago == '02' and nb_of_days < 30:
                    number_of_days = work_data['days']
                    if contract.septimo_dia:  # falta proporcional por septimo día
                        total_days = work_data['days'] + leave_days
                        if total_days != 7:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 7
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = 7 - leave_days
                        else:
                            number_of_days = work_data['days']
                    if contract.sept_dia:  # septimo día
                        if number_of_days == 0:
                            if leave_days != 7:

                                number_of_days = work_data['days']
                        if contract.semana_inglesa:
                            aux = number_of_days / 7 * 2
                        else:
                            aux = number_of_days - int(number_of_days)
                        _logger.info('number_of_days %s  aux %s',
                                     number_of_days, aux)
                        if aux > 0:
                            number_of_days -= aux
                        elif number_of_days > 0:
                            if contract.semana_inglesa:
                                aux = 2
                            else:
                                aux = 1
                            number_of_days -= aux
                        attendances = {
                            'name': _("Séptimo día"),
                            'sequence': 3,
                            'code': "SEPT",
                            'number_of_days': aux,
                            'number_of_hours': 0.0,
                            'contract_id': contract.id,
                        }
                        res.append(attendances)
                # calculo para nóminas mensuales
                elif contract.periodicidad_pago == '05':
                    if contract.tipo_pago == '01':
                        total_days = work_data['days'] + leave_days
                        if total_days != 30:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 30
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = 30 - leave_days
                    elif contract.tipo_pago == '03':
                        total_days = work_data['days'] + leave_days
                        if total_days != 30.42:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = 30.42
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] * \
                                    30.42 / 30 - leave_days
                            else:
                                number_of_days = 30.42 - leave_days
                        else:
                            number_of_days = work_data['days'] * 30.42 / 30
                    else:
                        dias_periodo = (datetime.strptime(
                            date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days + 1
                        total_days = work_data['days'] + leave_days
                        if total_days != dias_periodo:
                            if leave_days == 0 and not nvo_ingreso:
                                number_of_days = dias_periodo
                            elif nvo_ingreso:
                                number_of_days = work_data['days'] - leave_days
                            else:
                                number_of_days = dias_periodo - leave_days
                        else:
                            number_of_days = work_data['days']
                else:
                    number_of_days = work_data['days']
            else:
                date_start = contract.date_start
                date_start = datetime.strptime(date_start, "%Y-%m-%d")
                d_from = datetime.strptime(date_from, "%Y-%m-%d")
                d_to = datetime.strptime(date_to, "%Y-%m-%d")
                if date_start > d_from:
                    number_of_days = (d_to - date_start).days + 1 - leave_days
                else:
                    number_of_days = (d_to - d_from).days + 1 - leave_days
            attendances = {
                'name': _("Días de trabajo"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': number_of_days ,  # or number_of_days  work_data['days'],
                'number_of_hours': round(number_of_days*8,2),
                'contract_id': contract.id,
            }

            res.append(attendances)

            # Compute horas extas
            horas = horas_obj.search([('employee_id', '=', contract.employee_id.id), (
                'fecha', '>=', date_from), ('fecha', '<=', date_to), ('state', '=', 'done')])
            horas_by_tipo_de_horaextra = defaultdict(list)
            for h in horas:
                horas_by_tipo_de_horaextra[h.tipo_de_hora].append(h.horas)

            for tipo_de_hora, horas_set in horas_by_tipo_de_horaextra.items():
                work_code = tipo_de_hora_mapping.get(tipo_de_hora, '')
                number_of_days = len(horas_set)
                number_of_hours = sum(is_number(hs) for hs in horas_set)

                attendances = {
                    'name': _("Horas extras"),
                    'sequence': 2,
                    'code': work_code,
                    'number_of_days': number_of_days,
                    'number_of_hours': number_of_hours,
                    'contract_id': contract.id,
                }
                res.append(attendances)

            res.extend(leaves.values())

        return res

