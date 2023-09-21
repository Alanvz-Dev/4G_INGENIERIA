from odoo import _, api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import calendar


class FinancialReportEstadoFinanciero(models.Model):
    _name = 'financial_report.estados_financieros'
    _description = 'Estados Financieros'
    year =fields.Selection([ ('2020', '2020'),('2021', '2021'),('2022', '2022'),('2023', '2023')], default=datetime.now().strftime('%Y'))
    MONTH_LIST= [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),('12', 'Diciembre')]
    month = fields.Selection(MONTH_LIST, string='Month', required=True, default=MONTH_LIST[int(datetime.now().strftime('%m'))-1])
    start_date = fields.Date(string='Desde: ')
    end_date = fields.Date(string='Hasta: ')

    account_account_sel = fields.Many2many(
        'account.account', 'activos', 'id', string='Cuenta Contable')
    account_group_sel = fields.Many2many(
        'account.group', 'activos_group', 'id', string='Cuenta Contable Agrupadora')
    total_activo_circulante = fields.Float(string='Total :')

    account_account_sel_1 = fields.Many2many(
        'account.account', 'activos_nc', 'id', string='Cuenta Contable')
    account_group_sel_1 = fields.Many2many(
        'account.group', 'activos_nc_group', 'id', string='Cuenta Contable Agrupadora')
    total_activo_no_circulante = fields.Float(string='Total :')

    account_account_sel_2 = fields.Many2many(
        'account.account', 'pasivo_acp', 'id', string='Cuenta Contable')
    account_group_sel_2 = fields.Many2many(
        'account.group', 'pasivo_acp_group', 'id', string='Cuenta Contable Agrupadora')
    total_pasivo_a_corto_plazo = fields.Float(string='Total :')

    account_account_sel_3 = fields.Many2many(
        'account.account', 'capital_c', 'id', string='Cuenta Contable')
    account_group_sel_3 = fields.Many2many(
        'account.group', 'capital_c_group', 'id', string='Cuenta Contable Agrupadora')
    total_capital_contable = fields.Float(string='Total :')

    resultado_de_ejercicio_anterior = fields.Float(
        string='Resultado Del Ejercio Anterior: ')
    activo_y_activo_no_circulante = fields.Float(
        string='Total Activo \n+ Activo No Circulante: ')
    total_pasivo_y_capital_contable = fields.Float(
        string='Total Pasivo \n+ Capital Contable: ')

    binary = fields.Binary()
    binary_fname = fields.Char()

    def generar_reporte(self):
        activo_circulante = self.get_accounting_data()

    def get_accounting_data(record):
        start_end_dates=record.get_start_end_date()
        accounting_data = []
        activo_circulante = []
        activo_no_circulante = []
        pasivo_a_cortp_plazo = []
        capital_contable = []
        # Activo Circulante
        if record.account_account_sel:
            activo_circulante.append(record.get_dict_data(
                record.account_account_sel, start_end_dates[0], start_end_dates[1]))
        if record.account_group_sel:
            activo_circulante.append(record.get_dict_data(
                record.account_group_sel, start_end_dates[0], start_end_dates[1]))
        if activo_circulante:
            #record.total_activo_circulante = activo_circulante[0][-1]['Total']
            record.write({'total_activo_circulante':activo_circulante[0][-1]['Total']})
            record.update({'total_activo_circulante':activo_circulante[0][-1]['Total']}) 
        else:
            record.total_activo_circulante = 0

        # Activo No Circulante
        if record.account_account_sel_1:
            activo_no_circulante.append(record.get_dict_data(
                record.account_account_sel_1, start_end_dates[0], start_end_dates[1]))
        if record.account_group_sel_1:
            activo_no_circulante.append(record.get_dict_data(
                record.account_group_sel_1, start_end_dates[0], start_end_dates[1]))
        if activo_no_circulante:
            record.total_activo_no_circulante = activo_no_circulante[0][-1]['Total']
        else:
            record.total_activo_no_circulante = 0

        # Pasivo a Corto Plazo
        if record.account_account_sel_2:
            pasivo_a_cortp_plazo.append(record.get_dict_data(
                record.account_account_sel_2, start_end_dates[0], start_end_dates[1]))
        if record.account_group_sel_2:
            pasivo_a_cortp_plazo.append(record.get_dict_data(
                record.account_group_sel_2, start_end_dates[0], start_end_dates[1]))        
        if pasivo_a_cortp_plazo:
            record.total_pasivo_a_corto_plazo = pasivo_a_cortp_plazo[0][-1]['Total']
        else:
            record.total_pasivo_a_corto_plazo = 0

        


        # Capital Contable
        if record.account_account_sel_3:
            capital_contable.append(record.get_dict_data(
                record.account_account_sel_3, start_end_dates[0], start_end_dates[1]))
        if record.account_group_sel_3:
            capital_contable.append(record.get_dict_data(
                record.account_group_sel_3, start_end_dates[0], start_end_dates[1]))
        if capital_contable:
            record.total_capital_contable = capital_contable[0][-1]['Total'] + \
                record.resultado_de_ejercicio_anterior
        else:
            record.total_capital_contable = 0

        accounting_data.append(activo_circulante)
        accounting_data.append(activo_no_circulante)
        accounting_data.append(pasivo_a_cortp_plazo)
        accounting_data.append(capital_contable)

        record.total_pasivo_y_capital_contable = record.total_pasivo_a_corto_plazo + \
            record.total_capital_contable
        record.activo_y_activo_no_circulante = record.total_activo_circulante + \
            record.total_activo_no_circulante
        # Si no se realiza el retorno de esta forma, odoo lo interpretará como si del retorno de una vista se tratara
        return (accounting_data)


    def saldo_incial_global(self,codigo,fecha_final):

        query ="select sum(debit)-sum(credit) from account_move_line where move_id in (select id from account_move where contabilidad_electronica =true ) and account_id in (select id from account_account where code like '"+codigo+"%') and date between '2020-01-01' and '"+fecha_final+"'"
        o=self.env.cr.execute(query)
        print(o)
        x=self.env.cr.fetchone()
        if x[0] is None:
            return 0
        if x:
            return x[0]
        
    

    def get_start_end_date(self):        
        dateMonthStart = "%s-%s-01" % (int(self.year), int(self.month))
        dateMonthEnd = "%s-%s-%s" % (int(self.year), int(self.month),
                                     calendar.monthrange(int(self.year), int(self.month))[1])
        print("primer dia del mes: %s" % dateMonthStart)
        print("segundo dia del mes: %s" % dateMonthEnd)
        return (dateMonthStart, dateMonthEnd)

    def get_dict_data(record, account_group_or_account, start_date, end_date):


        financial_reports = account_group_or_account.env['financial_reports.detail']
        account_result = []
        acum_total_amount = 0
        if account_group_or_account._name == 'account.group':
            for account in account_group_or_account:
                amount = 0
                initial_balance=0
                try:
                    initial_balance=record.saldo_incial_global(account.code_prefix,end_date)
                except:
                    initial_balance=0
                try:
                    amount = initial_balance+financial_reports.result_by_account_group(
                account.code_prefix, start_date, end_date)
                except:
                    amount=0                
                account_result.append(
                    {'Cuenta': account.code_prefix, 'Nombre': account.name, 'Monto': amount})
                acum_total_amount = acum_total_amount+amount
        print(acum_total_amount)

        if account_group_or_account._name == 'account.account':
            for account in account_group_or_account:
                amount = 0
                initial_balance=0
                try:

                    initial_balance=record.saldo_incial_global(account.code_prefix,end_date)
                except:
                    initial_balance=0
                try:

                    amount = initial_balance+financial_reports.result_by_account_group(
                    account.code, start_date, end_date)
                except:
                    amount=0
                account_result.append(
                    {'Cuenta': account.code, 'Nombre': account.name, 'Monto': amount})
                acum_total_amount = acum_total_amount+amount
        
        #Balance Final
        account_result.append({'Total': acum_total_amount})

        return account_result


class EstadoFinancieroXlsxReport(models.AbstractModel):
    _name = 'report.financial_reports.estado_financiero'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        report_data = record.get_accounting_data()
        d = report_data[0][0][-1].get('Total')
        print(d)
        sheet = workbook.add_worksheet('Estado Financiero')
        bold = workbook.add_format({'bold': True})

        sheet.write(0, 0, self._cr.dbname, bold)
        sheet.write(1, 0, '', bold)
        sheet.write(3, 0, '', bold)
        sheet.write(3, 1, 'Monto', bold)
        actual_row = 8

        # Activo Circulante
        sheet.write(7, 0, 'Activo Circulante', bold)
        sheet.write(8, 0, '', bold)
        try:

            for item in range(len(report_data[0][0])):
                sheet.write(actual_row, 0, report_data[0][0][item].get('Cuenta'))
                sheet.write(actual_row, 2, report_data[0][0][item].get('Monto'))
                sheet.write(actual_row, 1, report_data[0][0][item].get('Nombre'))
                actual_row = actual_row+1
            actual_row = actual_row+1
            sheet.write(actual_row-2, 0, 'Total:', bold)
            sheet.write(actual_row-2, 1, report_data[0][0][-1].get('Total'), bold)
        except:
            print('err')
        # Activo No Circulante
        sheet.write(actual_row+1, 0, 'Activo No Circulante', bold)
        sheet.write(actual_row+2, 0, '', bold)
        actual_row = actual_row+2
        try:
            for item in range(len(report_data[1][0])):
                sheet.write(actual_row, 0, report_data[1][0][item].get('Cuenta'))
                sheet.write(actual_row, 2, report_data[1][0][item].get('Monto'))
                sheet.write(actual_row, 1, report_data[1][0][item].get('Nombre'))
                actual_row = actual_row+1
            actual_row = actual_row+1
            sheet.write(actual_row-2, 0, 'Total:', bold)
            sheet.write(actual_row-2, 1, report_data[1][0][-1].get('Total'), bold)
        except:
            print('err')
        # Pasivo a Corto Plazo
        sheet.write(actual_row+1, 0, 'Pasivo a Corto Plazo', bold)
        sheet.write(actual_row+2, 0, '', bold)
        actual_row = actual_row+2

        try:
            for item in range(len(report_data[2][0])):
                sheet.write(actual_row, 0, report_data[2][0][item].get('Cuenta'))
                sheet.write(actual_row, 2, report_data[2][0][item].get('Monto'))
                sheet.write(actual_row, 1, report_data[2][0][item].get('Nombre'))
                actual_row = actual_row+1
            actual_row = actual_row+1
            sheet.write(actual_row-2, 0, 'Total:', bold)
            sheet.write(actual_row-2, 1, report_data[2][0][-1].get('Total'), bold)
        except:
            print('err')


        # Capital Contable
        sheet.write(actual_row+1, 0, 'Capital Contable', bold)
        sheet.write(actual_row+2, 0, '', bold)
        actual_row = actual_row+2

        try:
            for item in range(len(report_data[3][0])):
                sheet.write(actual_row, 0, report_data[3][0][item].get('Cuenta'))
                sheet.write(actual_row, 2, report_data[3][0][item].get('Monto'))
                sheet.write(actual_row, 1, report_data[3][0][item].get('Nombre'))
                actual_row = actual_row+1
            actual_row = actual_row+1
            sheet.write(actual_row-2, 0,  'Resultado del ejercicio anterior')
            sheet.write(actual_row-2, 1, record.resultado_de_ejercicio_anterior)
            actual_row = actual_row+1
            sheet.write(actual_row-2, 0, 'Total:', bold)
            sheet.write(actual_row-2, 1, report_data[3][0][-1].get(
                'Total')+record.resultado_de_ejercicio_anterior, bold)
        except:
            print('err')
        print(report_data)
