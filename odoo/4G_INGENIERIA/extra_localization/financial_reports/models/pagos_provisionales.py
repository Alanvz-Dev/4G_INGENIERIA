import datetime
import calendar
from odoo import _, api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

class financial_months(models.Model):
    _name = 'financial.months'

    name = fields.Char()


class FinancialReportPagosProvisionales(models.Model):
    _name = 'financial_report.pagos_provisionales'
    _description = 'Pagos Provisionales'
    start_date = fields.Date()
    end_date = fields.Date()
    account_account_sel = fields.Many2many(
        comodel_name='account.account', string='Cuenta Contable')
    account_group_sel = fields.Many2many(
        comodel_name='account.group', string='Cuenta Contable Agrupadora')
    months_ids = fields.Many2many(
        'financial.months',
        string='Authors'
    )

    def btn_test(self):
        return self.env.ref('financial_reports.pagoisrc_report').report_action(self, data={}, config=False)        

    def get_data(self,record):
    #     return self.env.ref('financial_reports.pagoisrc_report').report_action(self, data={}, config=False)        

    # def get_data(self):

        dict_results={}
        results=[]
        
        for item in self.date_range(str(2021)):
            print(item)
            total_facturas=0
            total_notas_de_credito=0
            facturas_con_iva=self.env['account.invoice'].search([('type','=','out_invoice'),('state','in',['open','paid']),('date_invoice','>=',item[0]),('date_invoice','<=',item[1])])
            for factura in facturas_con_iva:
                total_facturas=total_facturas+factura.amount_untaxed_signed
            notas_de_credito=self.env['account.invoice'].search([('type','=','out_refund'),('state','in',['open','paid']),('date_invoice','>=',item[0]),('date_invoice','<=',item[1])])
            for factura2 in notas_de_credito:
                total_notas_de_credito=total_notas_de_credito+factura2.amount_untaxed_signed
            

            x = record.get_total_ingresos_nominales(item[0],item[1])
            
            results.append(x)
        return results
                    
        

    @api.multi
    def get_total_ingresos_nominales(self, start_date=False, end_date=False):
        print(self)
        arr_results=[]
        facturas=[]
        notas_de_credito_arr=[]
        json_res={'Periodo':"Del:"+start_date+"--Al--"+end_date,
        'cuentas':arr_results,
        'Facturas':facturas,
        'Notas de Credito':notas_de_credito_arr}
        report_result = []
        result_acumulado = 0.0
        result_by_month = 0.0
        individual_result = 0.0
        financial_tool = self.env['financial_reports.detail']
        for account_a in self.account_account_sel:
            individual_result = 0.0
            tmp_result = financial_tool.result_by_account_group(
                account_a.code, start_date, end_date)
            result_acumulado = result_acumulado+tmp_result
            individual_result = tmp_result
            result_by_month = result_by_month+individual_result
            report_result.append((account_a.code, individual_result))
            arr_results.append({'cuenta':account_a.code,'cantidad':individual_result})
        for account_g in self.account_group_sel:
            individual_result = 0.0
            tmp_result = financial_tool.result_by_account_group(
                account_g.code_prefix, start_date, end_date)
            result_acumulado = result_acumulado+tmp_result
            individual_result = tmp_result
            result_by_month = result_by_month+individual_result
            report_result.append((account_g.code_prefix, ))
            arr_results.append({'cuenta':account_g.code_prefix,'cantidad':individual_result})

        print(arr_results)
        print(report_result)
        total_facturas_iva=0
        total_facturas_sin_iva=0
        total_notas_de_credito_iva=0
        total_notas_de_credito_sin_iva=0



        facturas_con_iva=self.env['account.invoice'].search([('type','=','out_invoice'),('state','in',['open','paid']),('amount_tax','>',0),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        for factura in facturas_con_iva:
            total_facturas_iva=total_facturas_iva+factura.amount_untaxed_signed
            facturas.append({'Con IVA':factura.move_name,'cantidad':factura.amount_untaxed_signed or 0})

        facturas_sin_iva=self.env['account.invoice'].search([('type','=','out_invoice'),('state','in',['open','paid']),('amount_tax','<=',0),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        for factura in facturas_sin_iva:
            total_facturas_sin_iva=total_facturas_sin_iva+factura.amount_untaxed_signed
            facturas.append({'Sin IVA':factura.move_name,'cantidad':factura.amount_untaxed_signed})

        notas_de_credito_iva=self.env['account.invoice'].search([('type','=','out_refund'),('amount_tax','>',0),('state','in',['open','paid']),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        for nota_iva in notas_de_credito_iva:
            total_notas_de_credito_iva=total_notas_de_credito_iva+nota_iva.amount_untaxed_signed
            notas_de_credito_arr.append({'Notas de Crédito IVA':nota_iva.move_name,'cantidad':nota_iva.amount_untaxed_signed})


        notas_de_credito_sin_iva=self.env['account.invoice'].search([('type','=','out_refund'),('amount_tax','<=',0),('state','in',['open','paid']),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        for nota_iva in notas_de_credito_sin_iva:
            total_notas_de_credito_sin_iva=total_notas_de_credito_sin_iva+nota_iva.amount_untaxed_signed
            notas_de_credito_arr.append({'Notas de Crédito Sin IVA':nota_iva.move_name,'cantidad':nota_iva.amount_untaxed_signed})
    
        total_ingresos_nominales = result_by_month
        json_res.update({'ingresos nominales': result_by_month})
        json_res.update({'total cc del mes': result_by_month})
        json_res.update({'total ingresos nominales': total_ingresos_nominales+total_facturas_iva+total_facturas_sin_iva+total_notas_de_credito_iva+total_notas_de_credito_sin_iva})
        json_res.update({'total facturas con iva': total_facturas_iva})
        json_res.update({'total facturas sin iva': total_facturas_sin_iva})
        json_res.update({'total notas de credito con iva': total_notas_de_credito_iva})
        json_res.update({'total notas de credito sin iva': total_notas_de_credito_sin_iva})
        return json_res


    def date_range(self, anio):
        dates = []
        dates.append(self.get_start_end_date((anio+'-01-'+'01')))
        dates.append(self.get_start_end_date((anio+'-02-'+'01')))
        dates.append(self.get_start_end_date((anio+'-03-'+'01')))
        dates.append(self.get_start_end_date((anio+'-04-'+'01')))
        dates.append(self.get_start_end_date((anio+'-05-'+'01')))
        dates.append(self.get_start_end_date((anio+'-06-'+'01')))
        dates.append(self.get_start_end_date((anio+'-07-'+'01')))
        dates.append(self.get_start_end_date((anio+'-08-'+'01')))
        dates.append(self.get_start_end_date((anio+'-09-'+'01')))
        dates.append(self.get_start_end_date((anio+'-10-'+'01')))
        dates.append(self.get_start_end_date((anio+'-11-'+'01')))
        dates.append(self.get_start_end_date((anio+'-12-'+'01')))
        return dates

    def get_start_end_date(self, date_time_str):
        # '2021-02-01'
        today = datetime.datetime.strptime(date_time_str, DEFAULT_SERVER_DATE_FORMAT)
        dateMonthStart = "%s-%s-01" % (today.year, today.month)
        dateMonthEnd = "%s-%s-%s" % (today.year, today.month,
                                     calendar.monthrange(today.year, today.month)[1])
        print("primer dia del mes: %s" % dateMonthStart)
        print("segundo dia del mes: %s" % dateMonthEnd)
        return (dateMonthStart, dateMonthEnd)




class PagoIsrCXlsxReport(models.AbstractModel):
    _name = 'report.financial_reports.pagoisrc'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, record):
        print(workbook)
        print(data)
        print(record)
        data_arr=[]
        results=self.env['financial_report.pagos_provisionales'].get_data(record)
        mes=0
        cu=0.0282
        ingresos_nominales_acumulados=0.0
        utilidad_estimada_anterior=0.0
        for element in results:
            print(element)
            ingresos_nominales_acumulados=ingresos_nominales_acumulados+element['total ingresos nominales']
            utilidad_estimada=ingresos_nominales_acumulados*cu
            isr_causado_acumulado=utilidad_estimada*.30
            isr_a_pagar_de_mes=isr_causado_acumulado-utilidad_estimada_anterior
            utilidad_estimada_anterior=isr_causado_acumulado
            print(element['cuentas'])
            print('total cc del mes\t'+str(element['total cc del mes']))
            print('total ingresos nominales\t'+str(element['total ingresos nominales'])  )
            print('total facturas con iva\t'+str(element['total facturas con iva']) )
            print('total facturas sin iva\t'+str(element['total facturas sin iva']) )
            print('total notas de credito con iva\t'+str(element['total notas de credito con iva']) )
            print('total notas de credito sin iva\t'+str(element['total notas de credito sin iva']) )
            print('ingresos_nominales_acumulados\t'+str(ingresos_nominales_acumulados) )
            print('utilidad_estimada\t'+str(utilidad_estimada) )
            print('isr_causado_acumulado\t'+str(isr_causado_acumulado) )
            print('isr_a_pagar_de_mes\t'+str(isr_a_pagar_de_mes) )
            print('utilidad_estimada_anterior\t'+str(utilidad_estimada_anterior) )  

            data_arr.append({
                'cuentas':element['cuentas'],
                'ventas':element['ingresos nominales'],
                'total ingresos nominales':element['total ingresos nominales'],
                'ingresos_nominales_acumulados':ingresos_nominales_acumulados,

                'total cc del mes':element['total cc del mes'],
                'total facturas con iva':element['total facturas con iva'],
                'total facturas sin iva':element['total facturas sin iva'],
                'total notas de credito con iva':element['total notas de credito con iva'],
                'total notas de credito sin iva':element['total notas de credito sin iva'],
                
                'utilidad_estimada':utilidad_estimada,
                'isr_causado_acumulado':isr_causado_acumulado,
                'isr_a_pagar_de_mes':isr_a_pagar_de_mes,
                'utilidad_estimada_anterior':element['total cc del mes'],

            })
            print(data_arr)
        
        sheet = workbook.add_worksheet('PT 4G')
        bold = workbook.add_format({'bold': True})
        sheet.write(1,1, 'Cuentas', bold)
        sheet.write(2,1, 'Ventas', bold)
        sheet.write(3,1, 'Ingresos Nominales', bold)
        sheet.write(4,1,'Ingresos Nominales Acumulados', bold)
        sheet.write(5,1, 'Total de Cuentas Contables', bold)
        sheet.write(6,1, 'Total Facturas Con IVA', bold)
        sheet.write(7,1, 'Total Facturas Sin IVA', bold)
        sheet.write(8,1, 'Total Notas de Crédito Con IVA', bold)
        sheet.write(9,1, 'Total Notas de Crédito Sin IVA', bold)
        sheet.write(10,1, 'Utilidad Estimada', bold)
        sheet.write(11,1, 'ISR Causado Acumulado', bold)
        sheet.write(12,1, 'ISR a Pagar de Mes', bold)
        sheet.write(13,1, 'Utilidad Estimada Anterior', bold)
        
        row=1
        col=2
        for item in data_arr:
            print(item)
            for item2 in item.values():
                sheet.write(row,col, str(item2))
                row=row+1
            row=1
            col=col+1