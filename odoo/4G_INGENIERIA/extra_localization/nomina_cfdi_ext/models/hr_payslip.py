# -*- coding: utf-8 -*-

import base64
import json
import requests
from lxml import etree
import os
#import time

#from dateutil import relativedelta
from pytz import timezone

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from reportlab.graphics.barcode import createBarcodeDrawing #, getCodes
from reportlab.lib.units import mm
import logging
_logger = logging.getLogger(__name__)
import os
import pytz
from .tzlocal import get_localzone
from odoo import tools
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from collections import defaultdict
from datetime import timedelta, date



import xlwt
from xlwt import easyxf
import io
from docutils.nodes import line


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    def open_modification_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Recibos de Nómina",
            "view_mode": "form",
            "res_model": "nomina_cfdi.modify_slip",
            "target":"new",
            # "domain": [("id", "in", self.slip_ids.ids)],
            "context": {'create': False,'edit':False,'delete':False,'default_slips_ids': [(6,0,self.ids)]},
        }        
    @api.multi
    def hola(self):
        for data in self.web_progress_iter(self,msg="CULANDO NÓMINA"):  
            installment_ids = self.env['installment.line'].search(
                    [('employee_id', '=', data.employee_id.id), ('loan_id.state', '=', 'done'),
                     ('is_paid', '=', False),('date','<=',data.date_to)])
            if installment_ids:
                data.installment_ids = [(6, 0, installment_ids.ids)]
       

    @api.multi
    def compute_sheet(self):
        for payslip in self.web_progress_iter(self,msg="CULANDO NÓMINA PARTE 2"):
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
        return True




    @api.model
    def to_json_cfdi_3_0(self):
        payslip_total_TOP = 0
        payslip_total_TDED = 0
        payslip_total_PERG = 0
        payslip_total_PERE = 0
        payslip_total_SEIN = 0
        payslip_total_JPRE = 0

        if self.contract_id.date_end:
            antiguedad = int((datetime.strptime(self.contract_id.date_end, "%Y-%m-%d") -
                              datetime.strptime(self.contract_id.date_start, "%Y-%m-%d") + timedelta(days=1)).days/7)
        else:
            antiguedad = int((datetime.strptime(self.date_to, "%Y-%m-%d") - datetime.strptime(
                self.contract_id.date_start, "%Y-%m-%d") + timedelta(days=1)).days/7)

# **********  Percepciones ************
        #total_percepciones_lines = self.env['hr.payslip.line'].search(['|',('category_id.code','=','ALW'),('category_id.code','=','BASIC'),('category_id.code','=','ALW3'),('slip_id','=',self.id)])
        percepciones_grabadas_lines = self.env['hr.payslip.line'].search(
            ['|', ('category_id.code', '=', 'ALW'), ('category_id.code', '=', 'BASIC'), ('slip_id', '=', self.id)])
        #  percepciones_grabadas_lines = self.env['hr.payslip.line'].search([('slip_id','=',self.id)])
        lineas_de_percepcion = []
        lineas_de_percepcion_exentas = []
        percepciones_excentas_lines = 0
        _logger.info('Total conceptos %s id %s', len(
            percepciones_grabadas_lines), self.id)
        if percepciones_grabadas_lines:
            for line in percepciones_grabadas_lines:
                parte_exenta = 0
                parte_gravada = 0
                _logger.info('codigo %s monto %s',
                             line.salary_rule_id.code, line.total)

                if line.salary_rule_id.exencion:
                    percepciones_excentas_lines += 1
                    _logger.info(
                        'codigo %s', line.salary_rule_id.parte_gravada.code)
                    concepto_gravado = self.env['hr.payslip.line'].search(
                        [('code', '=', line.salary_rule_id.parte_gravada.code), ('slip_id', '=', self.id)], limit=1)
                    if concepto_gravado:
                        parte_gravada = concepto_gravado.total
                        _logger.info('total gravado %s',
                                     concepto_gravado.total)

                    _logger.info(
                        'codigo %s', line.salary_rule_id.parte_exenta.code)
                    concepto_exento = self.env['hr.payslip.line'].search(
                        [('code', '=', line.salary_rule_id.parte_exenta.code), ('slip_id', '=', self.id)], limit=1)
                    if concepto_exento:
                        parte_exenta = concepto_exento.total
                        _logger.info('total gravado %s', concepto_exento.total)

                    # horas extras
                    if line.salary_rule_id.tipo_cpercepcion.clave == '019':
                        percepciones_horas_extras = self.env['hr.payslip.worked_days'].search(
                            [('payslip_id', '=', self.id)])
                        if percepciones_horas_extras:
                            _logger.info('si hay ..')
                            for ext_line in percepciones_horas_extras:
                                #_logger.info('codigo %s.....%s ', line.code, ext_line.code)
                                if line.code == ext_line.code:
                                    if line.code == 'HEX1':
                                        tipo_hr = '03'
                                    elif line.code == 'HEX2':
                                        tipo_hr = '01'
                                    elif line.code == 'HEX3':
                                        tipo_hr = '02'
                                    lineas_de_percepcion_exentas.append({'TipoPercepcion': line.salary_rule_id.tipo_cpercepcion.clave,
                                                                         'Clave': line.code,
                                                                         'Concepto': line.salary_rule_id.name,
                                                                         'ImporteGravado': parte_gravada,
                                                                         'ImporteExento': parte_exenta,
                                                                         'Dias': ext_line.number_of_days,
                                                                         'TipoHoras': tipo_hr,
                                                                         'HorasExtra': ext_line.number_of_hours,
                                                                         'ImportePagado': line.total})

                    # Ingresos en acciones o títulos valor que representan bienes
                    elif line.salary_rule_id.tipo_cpercepcion.clave == '045':
                        lineas_de_percepcion_exentas.append({'TipoPercepcion': line.salary_rule_id.tipo_cpercepcion.clave,
                                                             'Clave': line.code,
                                                             'Concepto': line.salary_rule_id.name,
                                                             'ValorMercado': 56,
                                                             'PrecioAlOtorgarse': 48,
                                                             'ImporteGravado': parte_gravada,
                                                             'ImporteExento': parte_exenta})
                    else:
                        lineas_de_percepcion_exentas.append({'TipoPercepcion': line.salary_rule_id.tipo_cpercepcion.clave,
                                                             'Clave': line.code,
                                                             'Concepto': line.salary_rule_id.name,
                                                             'ImporteGravado': parte_gravada,
                                                             'ImporteExento': parte_exenta})
                else:
                    parte_gravada = line.total
                    lineas_de_percepcion.append({'TipoPercepcion': line.salary_rule_id.tipo_cpercepcion.clave,
                                                 'Clave': line.code,
                                                 'Concepto': line.salary_rule_id.name,
                                                 'ImporteGravado': line.total,
                                                 'ImporteExento': '0'})

                # if line.salary_rule_id.tipo_cpercepcion.clave != '022' and line.salary_rule_id.tipo_cpercepcion.clave != '023' and line.salary_rule_id.tipo_cpercepcion.clave != '025' and line.salary_rule_id.tipo_cpercepcion.clave !='039' and line.salary_rule_id.tipo_cpercepcion.clave !='044':
                payslip_total_PERE += round(parte_exenta, 2)
                payslip_total_PERG += round(parte_gravada, 2)
                if line.salary_rule_id.tipo_cpercepcion.clave == '022' or line.salary_rule_id.tipo_cpercepcion.clave == '023' or line.salary_rule_id.tipo_cpercepcion.clave == '025':
                    payslip_total_SEIN += round(line.total, 2)
                if line.salary_rule_id.tipo_cpercepcion.clave == '039' or line.salary_rule_id.tipo_cpercepcion.clave == '044':
                    payslip_total_JPRE += round(line.total, 2)

        percepcion = {
            'Totalpercepcion': {
                'TotalSeparacionIndemnizacion': payslip_total_SEIN,
                'TotalJubilacionPensionRetiro': payslip_total_JPRE,
                'TotalGravado': payslip_total_PERG,
                'TotalExento': payslip_total_PERE,
                'TotalSueldos': payslip_total_PERG + payslip_total_PERE - payslip_total_SEIN - payslip_total_JPRE,
            },
        }

        #************ SEPARACION / INDEMNIZACION   ************#
        if payslip_total_SEIN > 0:
            if payslip_total_PERG > self.contract_id.wage:
                ingreso_acumulable = self.contract_id.wage
            else:
                ingreso_acumulable = payslip_total_PERG
            if payslip_total_PERG - self.contract_id.wage < 0:
                ingreso_no_acumulable = 0
            else:
                ingreso_no_acumulable = payslip_total_PERG - self.contract_id.wage

            percepcion.update({
                'separacion': [{
                    'TotalPagado': payslip_total_SEIN,
                    'NumAñosServicio': self.contract_id.antiguedad_anos,
                    'UltimoSueldoMensOrd': self.contract_id.wage,
                    'IngresoAcumulable': ingreso_acumulable,
                    'IngresoNoAcumulable': ingreso_no_acumulable,
                }]
            })

            #percepcion.update({'SeparacionIndemnizacion': separacion})
        percepcion.update({'lineas_de_percepcion_grabadas': lineas_de_percepcion, 'no_per_grabadas': len(
            percepciones_grabadas_lines)-percepciones_excentas_lines})
        percepcion.update({'lineas_de_percepcion_excentas': lineas_de_percepcion_exentas,
                           'no_per_excentas': percepciones_excentas_lines})
        request_params = {'percepciones': percepcion}

# ****** OTROS PAGOS ******
        otrospagos_lines = self.env['hr.payslip.line'].search(
            [('category_id.code', '=', 'ALW3'), ('slip_id', '=', self.id)])
        #tipo_otro_pago_dict = dict(self.env['hr.salary.rule']._fields.get('tipo_otro_pago').selection)
        auxiliar_lines = self.env['hr.payslip.line'].search(
            [('category_id.code', '=', 'AUX'), ('slip_id', '=', self.id)])
        #tipo_otro_pago_dict = dict(self.env['hr.salary.rule']._fields.get('tipo_otro_pago').selection)
        lineas_de_otros = []
        if otrospagos_lines:
            for line in otrospagos_lines:
                # _#logger.info('line total ...%s', line.total)
                if line.salary_rule_id.tipo_cotro_pago.clave == '002':  # and line.total > 0:
                    #line2 = self.contract_id.env['tablas.subsidio.line'].search([('form_id','=',self.contract_id.tablas_cfdi_id.id),('lim_inf','<=',self.contract_id.wage)],order='lim_inf desc',limit=1)
                    self.subsidio_periodo = 0
                    #_logger.info('entro a este ..')
                    payslip_total_TOP += line.total
                    # if line2:
                    #    self.subsidio_periodo = (line2.s_mensual/self.imss_mes)*self.imss_dias
                    for aux in auxiliar_lines:
                        if aux.code == 'SUB':
                            self.subsidio_periodo = aux.total
                    _logger.info('subsidio aplicado %s importe excento %s',
                                 self.subsidio_periodo, line.total)
                    lineas_de_otros.append({'TipoOtrosPagos': line.salary_rule_id.tipo_cotro_pago.clave,
                                            'Clave': line.code,
                                            'Concepto': line.salary_rule_id.name,
                                            'ImporteGravado': '0',
                                            'ImporteExento': line.total,
                                            'SubsidioCausado': self.subsidio_periodo})
                else:
                    payslip_total_TOP += line.total
                    #_logger.info('entro al otro ..')
                    lineas_de_otros.append({'TipoOtrosPagos': line.salary_rule_id.tipo_cotro_pago.clave,
                                            'Clave': line.code,
                                            'Concepto': line.salary_rule_id.name,
                                            'ImporteGravado': '0',
                                            'ImporteExento': line.total})
        otrospagos = {
            'otrospagos': {
                'Totalotrospagos': payslip_total_TOP,
            },
        }
        otrospagos.update({'otros_pagos': lineas_de_otros,
                           'no_otros_pagos': len(otrospagos_lines)})
        request_params.update({'otros_pagos': otrospagos})

# ********** DEDUCCIONES *********
        total_imp_ret = 0
        suma_deducciones = 0
        self.importe_isr = 0
        self.isr_periodo = 0
        no_deuducciones = 0  # len(self.deducciones_lines)
        self.deducciones_lines = self.env['hr.payslip.line'].search(
            [('category_id.code', '=', 'DED'), ('slip_id', '=', self.id)])
        #ded_impuestos_lines = self.env['hr.payslip.line'].search([('category_id.name','=','Deducciones'),('code','=','301'),('slip_id','=',self.id)],limit=1)
        #tipo_deduccion_dict = dict(self.env['hr.salary.rule']._fields.get('tipo_deduccion').selection)
        # if ded_impuestos_lines:
        #   total_imp_ret = round(ded_impuestos_lines.total,2)
        lineas_deduccion = []
        if self.deducciones_lines:
            #_logger.info('entro deduciones ...')
            # todas las deducciones excepto imss e isr
            for line in self.deducciones_lines:
                if line.salary_rule_id.tipo_cdeduccion.clave != '001' and line.salary_rule_id.tipo_cdeduccion.clave != '002':
                    #_logger.info('linea  ...')
                    no_deuducciones += 1
                    lineas_deduccion.append({'TipoDeduccion': line.salary_rule_id.tipo_cdeduccion.clave,
                                             'Clave': line.code,
                                             'Concepto': line.salary_rule_id.name,
                                             'Importe': round(line.total, 2)})
                    payslip_total_TDED += round(line.total, 2)

            # todas las deducciones imss
            self.importe_imss = 0
            for line in self.deducciones_lines:
                if line.salary_rule_id.tipo_cdeduccion.clave == '001':
                    #_logger.info('linea imss ...')
                    self.importe_imss += round(line.total, 2)

            if self.importe_imss > 0:
                no_deuducciones += 1
                self.calculo_imss()
                lineas_deduccion.append({'TipoDeduccion': '001',
                                         'Clave': '302',
                                         'Concepto': 'Seguridad social',
                                         'Importe': round(self.importe_imss, 2)})
                payslip_total_TDED += round(self.importe_imss, 2)

            # todas las deducciones isr
            for line in self.deducciones_lines:
                if line.salary_rule_id.tipo_cdeduccion.clave == '002' and line.salary_rule_id.code == 'ISR':
                    self.isr_periodo = line.total
                if line.salary_rule_id.tipo_cdeduccion.clave == '002':
                    #_logger.info('linea ISR ...')
                    self.importe_isr += round(line.total, 2)

            if self.importe_isr > 0:
                no_deuducciones += 1
                lineas_deduccion.append({'TipoDeduccion': '002',
                                         'Clave': '301',
                                         'Concepto': 'ISR',
                                         'Importe': round(self.importe_isr, 2)})
                payslip_total_TDED += round(self.importe_isr, 2)
            total_imp_ret = round(self.importe_isr, 2)

        deduccion = {
            'TotalDeduccion': {
                'TotalOtrasDeducciones': round(payslip_total_TDED - total_imp_ret, 2),
                'TotalImpuestosRetenidos': total_imp_ret,
            },
        }
        deduccion.update(
            {'lineas_de_deduccion': lineas_deduccion, 'no_deuducciones': no_deuducciones})
        request_params.update({'deducciones': deduccion})

        #************ INCAPACIDADES  ************#
        incapacidades = self.env['hr.payslip.worked_days'].search(
            [('payslip_id', '=', self.id)])
        if incapacidades:
            for ext_line in incapacidades:
                if ext_line.code == 'INC_RT' or ext_line.code == 'INC_EG' or ext_line.code == 'INC_MAT':
                    _logger.info('codigo %s.... ', ext_line.code)
                    tipo_inc = ''
                    if ext_line.code == 'INC_RT':
                        tipo_inc = '01'
                    elif ext_line.code == 'INC_EG':
                        tipo_inc = '02'
                    elif ext_line.code == 'INC_MAT':
                        tipo_inc = '03'
                    incapacidad = {
                        'Incapacidad': {
                            'DiasIncapacidad': ext_line.number_of_days,
                            'TipoIncapacidad': tipo_inc,
                            'ImporteMonetario': 0,
                        },
                    }
                    request_params.update({'incapacidades': incapacidad})

        self.retencion_subsidio_pagado = self.isr_periodo - self.subsidio_periodo
        self.total_nomina = payslip_total_PERG + \
            payslip_total_PERE + payslip_total_TOP - payslip_total_TDED
        self.subtotal = payslip_total_PERG + payslip_total_PERE + payslip_total_TOP
        self.descuento = payslip_total_TDED

        work_days = 0
        lineas_trabajo = self.env['hr.payslip.worked_days'].search(
            [('payslip_id', '=', self.id)])
        for dias_pagados in lineas_trabajo:
            if dias_pagados.code == 'WORK100':
                work_days += dias_pagados.number_of_days
            if dias_pagados.code == 'FJC':
                work_days += dias_pagados.number_of_days
            if dias_pagados.code == 'SEPT':
                work_days += dias_pagados.number_of_days

        if self.tipo_nomina == 'O':
            self.periodicdad = self.contract_id.periodicidad_pago
        else:
            self.periodicdad = '99'
        diaspagados = 0
        if self.struct_id.name == 'Reparto de utilidades':
            diaspagados = 365
        else:
            diaspagados = work_days
        regimen = 0
        contrato = 0
        if self.struct_id.name == 'Liquidación - indemnizacion/finiquito':
            regimen = '13'
            contrato = '99'
        else:
            regimen = self.employee_id.regimen
            contrato = self.employee_id.contrato

        #************ JUBILACION / PENSION / RETIRO   ************#
        if payslip_total_JPRE > 0:
            if payslip_total_PERG > self.contract_id.wage:
                ingreso_acumulable_jpre = self.contract_id.wage
            else:
                ingreso_acumulable_jpre = payslip_total_PERG
            if payslip_total_PERG - self.contract_id.wage < 0:
                ingreso_no_acumulable_jpre = 0
            else:
                ingreso_no_acumulable_jpre = payslip_total_PERG - self.contract_id.wage

            percepcion.update({
                'jubilacion': [{
                    'TotalParcialidad': payslip_total_JPRE,
                    'MontoDiario': payslip_total_JPRE / diaspagados,
                    'IngresoAcumulable': ingreso_acumulable_jpre,
                    'IngresoNoAcumulable': ingreso_no_acumulable_jpre,
                }]
                # 'TotalUnaExhibicion'
            })

        # corregir hora
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.env.user.partner_id.tz or 'UTC'
        #timezone = tools.ustr(timezone).encode('utf-8')

        local = pytz.timezone(timezone)
        naive_from = datetime.now()
        local_dt_from = naive_from.replace(tzinfo=pytz.UTC).astimezone(local)
        date_from = local_dt_from.strftime("%Y-%m-%d %H:%M:%S")

        request_params.update({
            'factura': {
                'serie': self.company_id.serie_nomina,
                'folio': self.number_folio,
                'metodo_pago': self.methodo_pago,
                'forma_pago': self.forma_pago,
                'tipocomprobante': self.tipo_comprobante,
                'moneda': 'MXN',
                'tipodecambio': '1.0000',
                'fecha_factura': date_from,  # self.fecha_factura,
                'LugarExpedicion': self.company_id.zip,
                'RegimenFiscal': self.company_id.regimen_fiscal,
                'subtotal': self.subtotal,
                'descuento': self.descuento,
                'total': self.total_nomina,
            },
            'emisor': {
                'rfc': self.company_id.rfc,
                'curp': self.company_id.curp,
                'api_key': self.company_id.proveedor_timbrado,
                'modo_prueba': self.company_id.modo_prueba,
                'nombre_fiscal': self.company_id.nombre_fiscal,
                'telefono_sms': self.company_id.telefono_sms,
            },
            'receptor': {
                'rfc': self.employee_id.rfc,
                'nombre': self.employee_id.name,
                'uso_cfdi': self.uso_cfdi,
            },
            'conceptos': {
                'cantidad': '1.0',
                'ClaveUnidad': 'ACT',
                'ClaveProdServ': '84111505',
                'descripcion': 'Pago de nómina',
                'valorunitario': self.subtotal,
                'importe':  self.subtotal,
                'descuento': self.descuento,
            },
            'nomina12': {
                'TipoNomina': self.tipo_nomina,
                'FechaPago': self.fecha_pago,
                'FechaInicialPago': self.date_from,
                'FechaFinalPago': self.date_to,
                'NumDiasPagados': diaspagados,
                'TotalPercepciones': payslip_total_PERG + payslip_total_PERE,
                'TotalDeducciones': self.descuento,
                'TotalOtrosPagos': payslip_total_TOP,
            },
            'nomina12Emisor': {
                'RegistroPatronal': self.employee_id.registro_patronal,
                'RfcPatronOrigen': self.company_id.rfc,
            },
            'nomina12Receptor': {
                'ClaveEntFed': self.employee_id.estado.code,
                'Curp': self.employee_id.curp,
                'NumEmpleado': self.employee_id.no_empleado,
                'PeriodicidadPago': self.periodicdad,  # self.contract_id.periodicidad_pago,
                'TipoContrato': contrato,
                'TipoRegimen': regimen,
                'TipoJornada': self.employee_id.jornada,
                'Antiguedad': 'P' + str(antiguedad) + 'W',
                'Banco': self.employee_id.banco.c_banco,
                'CuentaBancaria': self.employee_id.no_cuenta,
                'FechaInicioRelLaboral': self.contract_id.date_start,
                'NumSeguridadSocial': self.employee_id.segurosocial,
                'Puesto': self.employee_id.job_id.name,
                'Departamento': self.employee_id.department_id.name,
                'RiesgoPuesto': self.contract_id.riesgo_puesto,
                'SalarioBaseCotApor': self.contract_id.sueldo_base_cotizacion,
                'SalarioDiarioIntegrado': self.contract_id.sueldo_diario_integrado,
            },
            'version': {
                'cfdi': '3.3',
                'sistema': 'odoo11',
                'version': '6',
            },
        })

# ****** CERTIFICADOS *******
        if not self.company_id.archivo_cer:
            raise UserError(_('Archivo .cer path is missing.'))
        if not self.company_id.archivo_key:
            raise UserError(_('Archivo .key path is missing.'))
        archivo_cer = self.company_id.archivo_cer
        archivo_key = self.company_id.archivo_key
        request_params.update({
            'certificados': {
                'archivo_cer': archivo_cer.decode("utf-8"),
                'archivo_key': archivo_key.decode("utf-8"),
                'contrasena': self.company_id.contrasena,
            }})
        print(request_params)
        return request_params


    @api.multi
    def action_cfdi_nomina_generate_cfdi_3_0(self):        
        for payslip in self:
            payslip.uso_cfdi='P01'
            if payslip.fecha_factura == False:
                payslip.fecha_factura = datetime.now()
                payslip.write({'fecha_factura': payslip.fecha_factura})
            if payslip.estado_factura == 'factura_correcta':
                raise UserError(
                    _('Error para timbrar factura, Factura ya generada.'))
            if payslip.estado_factura == 'factura_cancelada':
                raise UserError(
                    _('Error para timbrar factura, Factura ya generada y cancelada.'))

            values = payslip.to_json_cfdi_3_0()
            print(json.dumps(values, indent=4, sort_keys=True))
            if payslip.company_id.proveedor_timbrado == 'multifactura':
                url = '%s' % ('http://facturacion.itadmin.com.mx/api/nomina')
            elif payslip.company_id.proveedor_timbrado == 'multifactura2':
                url = '%s' % ('http://facturacion2.itadmin.com.mx/api/nomina')
            elif payslip.company_id.proveedor_timbrado == 'multifactura3':
                url = '%s' % ('http://facturacion3.itadmin.com.mx/api/nomina')
            elif payslip.company_id.proveedor_timbrado == 'gecoerp':
                if self.company_id.modo_prueba:
                    url = '%s' % (
                        'https://ws.gecoerp.com/itadmin/pruebas/nomina/?handler=OdooHandler33')
                else:
                    url = '%s' % (
                        'https://itadmin.gecoerp.com/nomina/?handler=OdooHandler33')
            print(json.dumps(values))
            response = requests.post(url, auth=None, verify=False, data=json.dumps(
                values), headers={"Content-type": "application/json"})

            _logger.info('something ... %s', response.text)
            json_response = response.json()
            xml_file_link = False
            estado_factura = json_response['estado_factura']
            if estado_factura == 'problemas_factura':
                raise UserError(_(json_response['problemas_message']))
            # Receive and stroe XML
            if json_response.get('factura_xml'):
                xml_file_link = payslip.company_id.factura_dir + \
                    '/' + payslip.number.replace('/', '_') + '.xml'
                xml_file = open(xml_file_link, 'w')
                xml_payment = base64.b64decode(json_response['factura_xml'])
                xml_file.write(xml_payment.decode("utf-8"))
                xml_file.close()
                payslip._set_data_from_xml_cfdi_3_0(xml_payment)

                xml_file_name = payslip.number.replace('/', '_') + '.xml'
                self.env['ir.attachment'].sudo().create(
                    {
                        'name': xml_file_name,
                        'datas': json_response['factura_xml'],
                        'datas_fname': xml_file_name,
                        'res_model': self._name,
                        'res_id': payslip.id,
                        'type': 'binary'
                    })
                report = self.env['ir.actions.report']._get_report_from_name(
                    'nomina_cfdi.report_payslip')
                report_data = report.render_qweb_pdf([payslip.id])[0]
                pdf_file_name = payslip.number.replace('/', '_') + '.pdf'
                self.env['ir.attachment'].sudo().create(
                    {
                        'name': pdf_file_name,
                        'datas': base64.b64encode(report_data),
                        'datas_fname': pdf_file_name,
                        'res_model': self._name,
                        'res_id': payslip.id,
                        'type': 'binary'
                    })

            payslip.write({'estado_factura': estado_factura,
                           'xml_nomina_link': xml_file_link,
                           'nomina_cfdi': True})


    @api.one
    def _set_data_from_xml_cfdi_3_0(self, xml_invoice):
        if not xml_invoice:
            return None
        NSMAP = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'cfdi': 'http://www.sat.gob.mx/cfd/3',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
        }

        xml_data = etree.fromstring(xml_invoice)
        Emisor = xml_data.find('cfdi:Emisor', NSMAP)
        RegimenFiscal = Emisor.find('cfdi:RegimenFiscal', NSMAP)
        Complemento = xml_data.find('cfdi:Complemento', NSMAP)
        TimbreFiscalDigital = Complemento.find(
            'tfd:TimbreFiscalDigital', NSMAP)

        self.rfc_emisor = Emisor.attrib['Rfc']
        self.name_emisor = Emisor.attrib['Nombre']
        self.tipocambio = xml_data.attrib['TipoCambio']
        #  self.tipo_comprobante = xml_data.attrib['TipoDeComprobante']
        self.moneda = xml_data.attrib['Moneda']
        self.numero_cetificado = xml_data.attrib['NoCertificado']
        self.cetificaso_sat = TimbreFiscalDigital.attrib['NoCertificadoSAT']
        self.fecha_certificacion = TimbreFiscalDigital.attrib['FechaTimbrado']
        self.selo_digital_cdfi = TimbreFiscalDigital.attrib['SelloCFD']
        self.selo_sat = TimbreFiscalDigital.attrib['SelloSAT']
        self.folio_fiscal = TimbreFiscalDigital.attrib['UUID']
        if self.number:
            self.folio = xml_data.attrib['Folio']
        if self.company_id.serie_nomina:
            self.serie_emisor = xml_data.attrib['Serie']
        self.invoice_datetime = xml_data.attrib['Fecha']
        self.version = TimbreFiscalDigital.attrib['Version']
        self.cadena_origenal = '||%s|%s|%s|%s|%s||' % (self.version, self.folio_fiscal, self.fecha_certificacion,
                                                       self.selo_digital_cdfi, self.cetificaso_sat)

        options = {'width': 275 * mm, 'height': 275 * mm}
        amount_str = str(self.total_nomina).split('.')
        # print 'amount_str, ', amount_str
        qr_value = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?&id=%s&re=%s&rr=%s&tt=%s.%s&fe=%s' % (self.folio_fiscal,
                                                                                                                          self.company_id.rfc,
                                                                                                                          self.employee_id.rfc,
                                                                                                                          amount_str[0].zfill(
                                                                                                                              10),
                                                                                                                          amount_str[1].ljust(
                                                                                                                              6, '0'),
                                                                                                                          self.selo_digital_cdfi[-8:],
                                                                                                                          )
        self.qr_value = qr_value
        ret_val = createBarcodeDrawing('QR', value=qr_value, **options)
        self.qrcode_image = base64.encodestring(ret_val.asString('jpg'))



    @api.multi
    def action_cfdi_nomina_generate(self):
        for payslip in self:
            payslip.uso_cfdi='CN01'
            if payslip.folio_fiscal:
                payslip.write({'nomina_cfdi': True, 'estado_factura': 'factura_correcta'})
                return True
            if payslip.fecha_factura == False:
                payslip.fecha_factura= datetime.now()
                payslip.write({'fecha_factura': payslip.fecha_factura})
            if payslip.estado_factura == 'factura_correcta':
                raise UserError(_('Error para timbrar factura, Factura ya generada.'))
            if payslip.estado_factura == 'factura_cancelada':
                raise UserError(_('Error para timbrar factura, Factura ya generada y cancelada.'))

            values = payslip.to_json()
            print(json.dumps(values, indent=4, sort_keys=True))
            if payslip.company_id.proveedor_timbrado == 'multifactura':
                url = '%s' % ('http://facturacion.itadmin.com.mx/api/nomina')
            elif payslip.company_id.proveedor_timbrado == 'multifactura2':
                url = '%s' % ('http://facturacion2.itadmin.com.mx/api/nomina')
            elif payslip.company_id.proveedor_timbrado == 'multifactura3':
                url = '%s' % ('http://facturacion3.itadmin.com.mx/api/nomina')
            elif payslip.company_id.proveedor_timbrado == 'gecoerp':
                if payslip.company_id.modo_prueba:
                    url = '%s' % ('https://ws.gecoerp.com/itadmin/pruebas/nomina/?handler=OdooHandler33')
                else:
                    url = '%s' % ('https://itadmin.gecoerp.com/nomina/?handler=OdooHandler33')
            else:
                raise UserError(_('Error, falta seleccionar el servidor de timbrado en la configuración de la compañía.'))

            try:
                response = requests.post(url , 
                                     auth=None,verify=False, data=json.dumps(values), 
                                     headers={"Content-type": "application/json"})
            except Exception as e:
                error = str(e)
                if "Name or service not known" in error or "Failed to establish a new connection" in error:
                    raise Warning("Servidor fuera de servicio, favor de intentar mas tarde")
                else:
                   raise Warning(error)

            if "Whoops, looks like something went wrong." in response.text:
                raise Warning("Error en el proceso de timbrado, espere un minuto y vuelva a intentar timbrar nuevamente. \nSi el error aparece varias veces reportarlo con la persona de sistemas.")

#            _logger.info('something ... %s', response.text)
            json_response = response.json()
            xml_file_link = False
            estado_factura = json_response['estado_factura']
            if estado_factura == 'problemas_factura':
                raise UserError(_(json_response['problemas_message']))
            # Receive and stroe XML 
            if json_response.get('factura_xml'):
                xml_file_link = payslip.company_id.factura_dir + '/' + payslip.number.replace('/','_') + '.xml'
                xml_file = open(xml_file_link, 'w')
                xml_payment = base64.b64decode(json_response['factura_xml'])
                xml_file.write(xml_payment.decode("utf-8"))
                xml_file.close()
                payslip._set_data_from_xml(xml_payment)
                    
                xml_file_name = payslip.number.replace('/','_') + '.xml'
                payslip.env['ir.attachment'].sudo().create(
                                            {
                                                'name': xml_file_name,
                                                'datas': json_response['factura_xml'],
                                                'datas_fname': xml_file_name,
                                                'res_model': payslip._name,
                                                'res_id': payslip.id,
                                                'type': 'binary'
                                            })	
                report = payslip.env['ir.actions.report']._get_report_from_name('nomina_cfdi.report_payslip')
                report_data = report.render_qweb_pdf([payslip.id])[0]
                pdf_file_name = payslip.number.replace('/','_') + '.pdf'
                payslip.env['ir.attachment'].sudo().create(
                                            {
                                                'name': pdf_file_name,
                                                'datas': base64.b64encode(report_data),
                                                'datas_fname': pdf_file_name,
                                                'res_model': payslip._name,
                                                'res_id': payslip.id,
                                                'type': 'binary'
                                            })

            payslip.write({'estado_factura': estado_factura,
                    'xml_nomina_link': xml_file_link,
                    'nomina_cfdi': True})

    @api.one
    def _set_data_from_xml(self, xml_invoice):
        if not xml_invoice:
            return None
        NSMAP = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
        }

        xml_data = etree.fromstring(xml_invoice)
        Complemento = xml_data.findall('cfdi:Complemento', NSMAP)

        for complementos in Complemento:
            TimbreFiscalDigital = complementos.find('tfd:TimbreFiscalDigital', NSMAP)
            if TimbreFiscalDigital:
                break

        self.tipocambio = xml_data.find('TipoCambio') and xml_data.attrib['TipoCambio'] or '1'
        self.moneda = xml_data.attrib['Moneda']
        self.numero_cetificado = xml_data.attrib['NoCertificado']
        self.cetificaso_sat = TimbreFiscalDigital.attrib['NoCertificadoSAT']
        self.fecha_certificacion = TimbreFiscalDigital.attrib['FechaTimbrado']
        self.selo_digital_cdfi = TimbreFiscalDigital.attrib['SelloCFD']
        self.selo_sat = TimbreFiscalDigital.attrib['SelloSAT']
        self.folio_fiscal = TimbreFiscalDigital.attrib['UUID']
     #   if self.number:
     #       self.folio = xml_data.attrib['Folio']
     #   if self.company_id.serie_nomina:
     #       self.serie_emisor = xml_data.attrib['Serie']
        self.invoice_datetime = xml_data.attrib['Fecha']
        version = TimbreFiscalDigital.attrib['Version']
        self.cadena_origenal = '||%s|%s|%s|%s|%s||' % (version, self.folio_fiscal, self.fecha_certificacion,
                                                       self.selo_digital_cdfi, self.cetificaso_sat)

        options = {'width': 275 * mm, 'height': 275 * mm}
        amount_str = str(self.total_nomina).split('.')
        qr_value = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?&id=%s&re=%s&rr=%s&tt=%s.%s&fe=%s' % (
            self.folio_fiscal,
            self.company_id.rfc,
            self.employee_id.rfc,
            amount_str[0].zfill(10),
            amount_str[1].ljust(6, '0'),
            self.selo_digital_cdfi[-8:],
        )
        self.qr_value = qr_value
        ret_val = createBarcodeDrawing('QR', value=qr_value, **options)
        self.qrcode_image = base64.encodestring(ret_val.asString('jpg'))




    @api.multi
    def export_report_xlsx(self):
        import base64
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Listado de nomina')
        header_style = easyxf('font:height 200; align: horiz center; font:bold True;' "borders: top thin,left thin,right thin,bottom thin")
        text_bold_left = easyxf('font:height 200; font:bold True; align: horiz left;' "borders: top thin,bottom thin")
        text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin")
        text_bold_right = easyxf('font:height 200;font:bold True; align: horiz right;' "borders: top thin,bottom thin")
        worksheet.write(0, 0, 'Cod', header_style)
        worksheet.write(0, 1, 'Empleado', header_style)
        worksheet.write(0, 2, 'Dias Pag', header_style)
        col_nm = 3
        all_column = self.get_all_columns()
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        for col in all_col_list:
            worksheet.write(0, col_nm, all_col_dict[col], header_style)
            col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            worksheet.write(0, col_nm, t, header_style)
            col_nm += 1
        
        payslip_group_by_department = self.get_payslip_group_by_department()[0]
        row = 1
        grand_total = {}

        
        for dept in self.web_progress_iter(payslip_group_by_department.keys(),msg="GENERANDO REPORTE DE NÓMINA"):
            row += 1
            worksheet.write_merge(row, row, 0, 2, self.env['hr.department'].browse(dept).name, text_bold_left)
            total = {}
            row += 1
            for slip in payslip_group_by_department[dept]:
                if slip.state == "cancel":
                    continue
                if slip.employee_id.no_empleado:
                    worksheet.write(row, 0, slip.employee_id.no_empleado, text_left)
                worksheet.write(row, 1, slip.employee_id.name, text_left)
                work_day = slip.get_total_work_days()[0]
                worksheet.write(row, 2, work_day, text_right)
                code_col = 3
                for code in all_col_list:
                    amt = 0
                    if code in total.keys():
                        amt = slip.get_amount_from_rule_code(code)[0]
                        if amt:
                            grand_total[code] = grand_total.get(code) + amt
                            total[code] = total.get(code) + amt
                    else:
                        amt = slip.get_amount_from_rule_code(code)[0]
                        total[code] = amt or 0
                        if code in grand_total.keys():
                            grand_total[code] = amt + grand_total.get(code) or 0.0
                        else:
                            grand_total[code] = amt or 0
                    worksheet.write(row, code_col, amt, text_right)
                    code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('001')[0], text_right)
                code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('002')[0], text_right)
                row += 1
            worksheet.write_merge(row, row, 0, 2, 'Total Departamento', text_bold_left)
            code_col = 3
            for code in all_col_list:
                worksheet.write(row, code_col, total.get(code), text_bold_right)
                code_col += 1
        row += 1
        worksheet.write_merge(row, row, 0, 2, 'Gran Total', text_bold_left)
        code_col = 3
        for code in all_col_list:
            worksheet.write(row, code_col, grand_total.get(code), text_bold_right)
            code_col += 1

        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        self.write({'file_data': base64.b64encode(data)})
        action = {
            'name': 'Journal Entries',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=hr.payslip.run&id=" + str(self.id) + "&field=file_data&download=true&filename=Listado_de_nomina.xls",
            'target': 'self',
            }
        return action


    @api.multi
    def action_cfdi_cancel(self):
        for item in self:
            if item.uso_cfdi=='P01':
                self.action_cfdi_cancel_4g()                
            elif item.uso_cfdi=='CN01':
                self.action_cfdi_cancel()
        return True

    @api.multi
    def action_cfdi_cancel_4_0(self):
        for payslip in self:
            if payslip.nomina_cfdi:
                if payslip.estado_factura == 'factura_cancelada':
                    pass
                    # raise UserError(_('La factura ya fue cancelada, no puede volver a cancelarse.'))
                if not payslip.company_id.archivo_cer:
                    raise UserError(_('Falta la ruta del archivo .cer'))
                if not payslip.company_id.archivo_key:
                    raise UserError(_('Falta la ruta del archivo .key'))
                archivo_cer = payslip.company_id.archivo_cer
                archivo_key = payslip.company_id.archivo_key
                archivo_xml_link = payslip.company_id.factura_dir + '/' + payslip.number.replace('/','_') + '.xml'
                with open(archivo_xml_link, 'rb') as cf:
                    archivo_xml = base64.b64encode(cf.read())
                values = {
                          'rfc': payslip.company_id.rfc,
                          'api_key': payslip.company_id.proveedor_timbrado,
                          'uuid': payslip.folio_fiscal,
                          'folio': payslip.folio,
                          'serie_factura': payslip.company_id.serie_nomina,
                          'modo_prueba': payslip.company_id.modo_prueba,
                            'certificados': {
                                  'archivo_cer': archivo_cer.decode("utf-8"),
                                  'archivo_key': archivo_key.decode("utf-8"),
                                  'contrasena': payslip.company_id.contrasena,
                            },
                          'xml': archivo_xml.decode("utf-8"),
                          'motivo': payslip.env.context.get('motivo_cancelacion',False),
                          'foliosustitucion': payslip.env.context.get('foliosustitucion',''),
                          }
                if payslip.company_id.proveedor_timbrado == 'multifactura':
                    url = '%s' % ('http://facturacion.itadmin.com.mx/api/refund')
                elif payslip.company_id.proveedor_timbrado == 'multifactura2':
                    url = '%s' % ('http://facturacion2.itadmin.com.mx/api/refund')
                elif payslip.company_id.proveedor_timbrado == 'multifactura3':
                    url = '%s' % ('http://facturacion3.itadmin.com.mx/api/refund')
                elif payslip.company_id.proveedor_timbrado == 'gecoerp':
                    if payslip.company_id.modo_prueba:
                        url = '%s' % ('https://ws.gecoerp.com/itadmin/pruebas/refund/?handler=OdooHandler33')
                    else:
                        url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                else:
                    raise UserError(_('Error, falta seleccionar el servidor de timbrado en la configuración de la compañía.'))

                try:
                    print(json.dumps(values))
                    response = requests.post(url , 
                                         auth=None,verify=False, data=json.dumps(values), 
                                         headers={"Content-type": "application/json"})
                except Exception as e:
                    error = str(e)
                    if "Name or service not known" in error or "Failed to establish a new connection" in error:
                        raise Warning("Servidor fuera de servicio, favor de intentar mas tarde")
                    else:
                       raise Warning(error)

                if "Whoops, looks like something went wrong." in response.text:
                    raise Warning("Error en el proceso de timbrado, espere un minuto y vuelva a intentar timbrar nuevamente. \nSi el error aparece varias veces reportarlo con la persona de sistemas.")

                json_response = response.json()
                #_logger.info('log de la exception ... %s', response.text)

                if json_response['estado_factura'] == 'problemas_factura':
                    raise UserError(_(json_response['problemas_message']))
                elif json_response.get('factura_xml', False):
                    if payslip.number:
                        xml_file_link = payslip.company_id.factura_dir + '/CANCEL_' + payslip.number.replace('/','_') + '.xml'
                    else:
                        raise UserError(_('La nómina no tiene nombre'))
                    xml_file = open(xml_file_link, 'w')
                    xml_invoice = base64.b64decode(json_response['factura_xml'])
                    xml_file.write(xml_invoice.decode("utf-8"))
                    xml_file.close()
                    if payslip.number:
                        file_name = payslip.number.replace('/','_') + '.xml'
                    else:
                        file_name = self.number.replace('/','_') + '.xml'
                    self.env['ir.attachment'].sudo().create(
                                                {
                                                    'name': file_name,
                                                    'datas': json_response['factura_xml'],
                                                    'datas_fname': file_name,
                                                    'res_model': self._name,
                                                    'res_id': payslip.id,
                                                    'type': 'binary'
                                                })
                payslip.write({'estado_factura': json_response['estado_factura']})


    @api.multi
    def action_cfdi_cancel_4g(self):
        for payslip in self:
            if payslip.nomina_cfdi:
                if payslip.estado_factura == 'factura_cancelada':
                    pass
                    # raise UserError(_('La factura ya fue cancelada, no puede volver a cancelarse.'))
                if not payslip.company_id.archivo_cer:
                    raise UserError(_('Falta la ruta del archivo .cer'))
                if not payslip.company_id.archivo_key:
                    raise UserError(_('Falta la ruta del archivo .key'))
                archivo_cer = payslip.company_id.archivo_cer
                archivo_key = payslip.company_id.archivo_key
                archivo_xml_link = payslip.company_id.factura_dir + \
                    '/' + payslip.number.replace('/', '_') + '.xml'
                with open(archivo_xml_link, 'rb') as cf:
                    archivo_xml = base64.b64encode(cf.read())
                print(payslip.folio_fiscal)
                values = {
                    'rfc': payslip.company_id.rfc,
                    'api_key': payslip.company_id.proveedor_timbrado,
                    'uuid': payslip.folio_fiscal,
                    'folio': payslip.folio,
                    'serie_factura': payslip.company_id.serie_nomina,
                    'modo_prueba': payslip.company_id.modo_prueba,
                    'certificados': {
                        'archivo_cer': archivo_cer.decode("utf-8"),
                        'archivo_key': archivo_key.decode("utf-8"),
                        'contrasena': payslip.company_id.contrasena,
                    },
                    'xml': archivo_xml.decode("utf-8"),
                }
                print(payslip.company_id)
                if payslip.company_id.proveedor_timbrado == 'multifactura':
                    url = '%s' % (
                        'http://facturacion.itadmin.com.mx/api/refund')
                elif payslip.company_id.proveedor_timbrado == 'multifactura2':
                    url = '%s' % (
                        'http://facturacion2.itadmin.com.mx/api/refund')
                elif payslip.company_id.proveedor_timbrado == 'multifactura3':
                    url = '%s' % (
                        'http://facturacion3.itadmin.com.mx/api/refund')
                elif payslip.company_id.proveedor_timbrado == 'gecoerp':
                    if payslip.company_id.modo_prueba:
                        url = '%s' % (
                            'https://ws.gecoerp.com/itadmin/pruebas/refund/?handler=OdooHandler33')
                        #url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                    else:
                        url = '%s' % (
                            'https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                print(json.dumps(values))
                response = requests.post(url,
                                         auth=None, verify=False, data=json.dumps(values),
                                         headers={"Content-type": "application/json"})

                # print 'Response: ', response.status_code
                json_response = response.json()
                print(json_response)
                #_logger.info('log de la exception ... %s', response.text)

                if json_response['estado_factura'] == 'problemas_factura':
                    raise UserError(_(json_response['problemas_message']))
                elif json_response.get('factura_xml', False):
                    if payslip.number:
                        xml_file_link = payslip.company_id.factura_dir + \
                            '/CANCEL_' + \
                            payslip.number.replace('/', '_') + '.xml'
                    else:
                        raise UserError(_('La nómina no tiene nombre'))
                    xml_file = open(xml_file_link, 'w')
                    xml_invoice = base64.b64decode(
                        json_response['factura_xml'])
                    xml_file.write(xml_invoice.decode("utf-8"))
                    xml_file.close()
                    if payslip.number:
                        file_name = payslip.number.replace('/', '_') + '.xml'
                    else:
                        file_name = self.number.replace('/', '_') + '.xml'
                    self.env['ir.attachment'].sudo().create(
                        {
                            'name': file_name,
                            'datas': json_response['factura_xml'],
                            'datas_fname': file_name,
                            'res_model': self._name,
                            'res_id': payslip.id,
                            'type': 'binary'
                        })
                payslip.write(
                    {'estado_factura': json_response['estado_factura']})