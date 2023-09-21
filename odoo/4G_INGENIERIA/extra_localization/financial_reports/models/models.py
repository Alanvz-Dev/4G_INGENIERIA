# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.modules.registry import Registry






class financial_detail(models.Model):
    _name = 'financial_reports.detail'
    
    start_date=fields.Date()
    end_date=fields.Date()
    acumulado=fields.Boolean()
    ce_asientos_contables = fields.Boolean()#Move lines
    ce_apuntes_contables = fields.Boolean()#Moves
    tipo = fields.Selection([('pyg', 'Pérdidas y Ganancias'), ('other', 'Otro')], string='Tipo de Reporte:', default='other')
    financial_reports_lines = fields.One2many(
        'financial_reports.line', 'financial_reports_detail_fk', ondelete="cascade")
    author_ids = fields.Many2many(
        'account.group',
        string='Authors'
    )


# class financial_detail(models.Model):
#     _name = 'financial_reports.months'
#     name=fields.Date()


    @api.multi
    def perdidas_y_ganancias_report(self):

        return self.env.ref('financial_reports.perdidasyganancias_report').report_action(self, data={}, config=False)
        
        
 
    def result_by_account_group(self,code_prefix,date_from,date_to,return_only_credit_or_debit=False):
        if code_prefix=='1-140':
            print('XCXX')
        group_or_account=''
        account_group=self.env['account.group'].search([('code_prefix','=',code_prefix)])
        if account_group:
            group_or_account=account_group.compute_account_ids
        if not account_group:
            group_or_account=self.env['account.account'].search([('code','=',code_prefix)])  
        account_move_line =self.env['account.move.line']  
        account_move =self.env['account.move']       
        no_deprecated_account_ids=[]
        move_ids_debito=[]
        move_ids_credito=[]
        credit=[]
        debit=[]
        for account in group_or_account:
            if account.deprecated==False:
                no_deprecated_account_ids.append(account.id)
            moves=account_move.search([('contabilidad_electronica','=',True),('state','=','posted'),('date', '>=',date_from),('date', '<=',date_to)]).ids
            move_lines=account_move_line.search(['&',('contabilidad_electronica','=',True),('date', '>=',date_from),('date', '<=',date_to), ('move_id','in',moves), ('account_id','in',no_deprecated_account_ids)])


            for move in move_lines:
                if move.credit>0.0:
                    credit.append(float("{:.2f}".format(move.credit)))
                    move_ids_credito.append(move.move_id.id)
                    
                if move.debit>0.0:
                    debit.append(float("{:.2f}".format(move.debit)))
                    move_ids_debito.append(move.move_id.id)

        result = 0.0
        try:
            credit.append(0.0)
            debit.append(0.0)
            if account_group.cuenta_tipo=='A':
                result=sum(credit)-sum(debit)
            elif account_group.cuenta_tipo=='D':
                result=sum(debit)-sum(credit)
            elif group_or_account.cuenta_tipo=='A':
                result=sum(credit)-sum(debit)
            elif group_or_account.cuenta_tipo=='D':
                result=sum(debit)-sum(credit)
            if not account_group.cuenta_tipo and not group_or_account.cuenta_tipo:
                raise UserError('La cuenta agrupadora '+account_group.code_prefix+""" no tiene cinfigurado el tipo (Acreedora o Deudora)""")
        except:

            raise UserError("""Ha ocurrido un error""")
            
                
        
        print(sum(debit))
        print(sum(credit))

        debitos=sum(debit)
        if return_only_credit_or_debit=='debit':
            return sum(debit)
        if return_only_credit_or_debit=='credit':
            return sum(credit)


        print('Cuenta:'+'\t'+code_prefix+'\t'+'Resultado:'+'\t'+str(result))
        return result



    def get_initial_balance(self,account_code_prefix,start_date,end_date):
        self.env.cr.execute("""select sum(debit)-sum(credit) from account_move_line where move_id in (select id from account_move where contabilidad_electronica =true ) and account_id in (select id from account_account where code like '"""+account_code_prefix+"""%') and date between '"""+start_date+"""' and '"""+end_date+"""'""")
        report_details = self.env.cr.fetchall()
        return report_details[0][0]

class financial_reports(models.Model):
    _name = 'financial_reports.line'
    financial_reports_detail_fk = fields.Many2one('financial_reports.detail', ondelete="cascade")
    account_group = fields.Many2one('account.group')
    debit = fields.Float()
    credit = fields.Float()
    balance = fields.Float()
    tipo = fields.Char()




class PerdidasYGananciasXlsxReport(models.AbstractModel):
    _name = 'report.financial_reports.perdidasyganancias'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, record):

        if self.env.cr.dbname=='RACKING_STORAGE_SYSTEM':
            financial_reports=self.env['financial_reports.detail']
            print(self)
            #Ferrextool
            Ventas_F=financial_reports.result_by_account_group('4-100',record.start_date,record.end_date)
            Devoluciones_y_Descuentos_sobre_ventas_F=financial_reports.result_by_account_group('4-200',record.start_date,record.end_date)
            Gastos_de_Administracion_F=financial_reports.result_by_account_group('5-200',record.start_date,record.end_date)
            Intereses_Bancarios_A_Cargo_F=financial_reports.result_by_account_group('5-400-001',record.start_date,record.end_date)
            Perdida_Cambiaria_F=financial_reports.result_by_account_group('5-400-002',record.start_date,record.end_date)
            Comisiones_Bancarias_F=financial_reports.result_by_account_group('5-400-004',record.start_date,record.end_date)
            Otros_Productos_F=financial_reports.result_by_account_group('4-400',record.start_date,record.end_date)
            Otros_Gastos_F=financial_reports.result_by_account_group('5-500',record.start_date,record.end_date)
            r1_f=Ventas_F-Devoluciones_y_Descuentos_sobre_ventas_F
            r2_f=(Ventas_F-Devoluciones_y_Descuentos_sobre_ventas_F)-Gastos_de_Administracion_F
            r3_f=Intereses_Bancarios_A_Cargo_F+Perdida_Cambiaria_F+Comisiones_Bancarias_F
            r4_f=Otros_Productos_F-Otros_Gastos_F
            sheet = workbook.add_worksheet('ESTADO DE PÉRDIDAS Y GANANCIAS')
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, 'CUENTA AGRUPADORA', bold)
            sheet.write(0, 1, 'CONCEPTO', bold)
            sheet.write(0, 2, 'BALANCE', bold)   
            data=[]
            data.append(('4-100','VENTAS',Ventas_F))
            data.append(('4-200','DESCUENTOS Y DEVOLUCIONES SOBRE VENTAS',Devoluciones_y_Descuentos_sobre_ventas_F))
            data.append(('','TOTAL INGRESOS',r1_f))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('5-200','GASTOS DE ADMINISTRACIÓN',Gastos_de_Administracion_F))
            data.append(('','RESULTADO DE OPERACIÓN',r2_f))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('5-400-001','INTERESES BANCARIOS A CARGO',Intereses_Bancarios_A_Cargo_F))
            data.append(('5-400-002','PERDIDA CAMBIARIA',Perdida_Cambiaria_F))
            data.append(('5-400-004','COMISIONES BANCARIAS',Comisiones_Bancarias_F))
            data.append(('','TOTAL R I F',r3_f))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('7300-000-000','OTROS PRODUCTOS',Otros_Productos_F))
            data.append(('7400-002-000','OTROS GASTOS',Otros_Gastos_F))
            data.append(('','TOTAL PARTIDAS EXTRAORDINARIAS',r4_f))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('','RESULTADO ANTES DE IMPUESTOS Y PTU',(r2_f-r3_f)+r4_f))
            #row col
            for row in range(len(data)):
                for col in range(len(data[row])):
                    print(data[row][col])
                    sheet.write(row+1, col, data[row][col])


        if self.env.cr.dbname=='CORPORATIVO_4G':
            financial_reports=self.env['financial_reports.detail']
            print(self)
            #Ferrextool
            Servicios_C=financial_reports.result_by_account_group('4-100',record.start_date,record.end_date)
            Otros_Ingresos_C=financial_reports.result_by_account_group('4-200',record.start_date,record.end_date)
            Gastos_de_Sueldos_C=financial_reports.result_by_account_group('5-101',record.start_date,record.end_date)
            Gastos_de_Administracion_C=financial_reports.result_by_account_group('5-102',record.start_date,record.end_date)
            Gastos_de_Ventas_C=financial_reports.result_by_account_group('5-201',record.start_date,record.end_date)
            
            
            
            r1_c=Servicios_C+Otros_Ingresos_C
            r2_c=Gastos_de_Sueldos_C+Gastos_de_Administracion_C+Gastos_de_Ventas_C
            r3_c=r1_c-r2_c
    
            sheet = workbook.add_worksheet('ESTADO DE PÉRDIDAS Y GANANCIAS')
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, 'CUENTA AGRUPADORA', bold)
            sheet.write(0, 1, 'CONCEPTO', bold)
            sheet.write(0, 2, 'BALANCE', bold)   
            data=[]
            data.append(('4-100','SERVICIOS',Servicios_C))
            data.append(('4-200','OTROS INGRESOS',Otros_Ingresos_C))
            data.append(('','TOTAL INGRESOS',r1_c))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('5-101','GASTOS DE SUELDOS',Gastos_de_Sueldos_C))
            data.append(('5-102','GASTOS DE ADMINISTRACIÓN',Gastos_de_Administracion_C))
            data.append(('5-201','GASTOS DE VENTA',Gastos_de_Ventas_C))
            data.append(('','Utilidad o Perdida del Ejercicio ',r3_c))
            #row col
            for row in range(len(data)):
                for col in range(len(data[row])):
                    print(data[row][col])
                    sheet.write(row+1, col, data[row][col])



        if self.env.cr.dbname=='4G_INGENIERIA':
            financial_reports=self.env['financial_reports.detail']
            print(self)
            #4G
            Ventas_Netas=financial_reports.result_by_account_group('4-100',record.start_date,record.end_date) #Credito - debito 15864549.449999997 
            Costo_De_Ventas=financial_reports.result_by_account_group('5-100',record.start_date,record.end_date)
            r1= Ventas_Netas-Costo_De_Ventas
            r2=0.0
            gastos_de_administracion=financial_reports.result_by_account_group('5-200-001',record.start_date,record.end_date)#Debito-Credito 1900208.4799999995
            gastos_de_operacion=financial_reports.result_by_account_group('5-200-002',record.start_date,record.end_date) 
            gastos_sistemas=financial_reports.result_by_account_group('5-200-003',record.start_date,record.end_date) 
            gastos_de_ventas=financial_reports.result_by_account_group('5-300',record.start_date,record.end_date)
            r2=(gastos_de_ventas+gastos_de_administracion+gastos_de_operacion+gastos_sistemas)
            r3=r1-r2
            #r4=0.0
            productos_financieros=financial_reports.result_by_account_group('4-300',record.start_date,record.end_date)
            gastos_financieros=financial_reports.result_by_account_group('5-400',record.start_date,record.end_date) 
            #RIF
            r4=productos_financieros-gastos_financieros
            otros_ingresos=financial_reports.result_by_account_group('4-400',record.start_date,record.end_date) 
            otros_gastos=financial_reports.result_by_account_group('5-500',record.start_date,record.end_date) 
            r5=otros_ingresos-otros_gastos
            r6=r3+r4+r5 
            sheet = workbook.add_worksheet('ESTADO DE PÉRDIDAS Y GANANCIAS')
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, 'CUENTA AGRUPADORA', bold)
            sheet.write(0, 1, 'CONCEPTO', bold)
            sheet.write(0, 2, 'BALANCE', bold)
            #row col
            sheet.write(2, 0,'4-100') 
            sheet.write(3, 0, '5-100')        
            sheet.write(2, 1,'VENTAS NETAS')
            sheet.write(2, 2,Ventas_Netas)
            sheet.write(3, 1, 'COSTO DE VENTAS')
            sheet.write(3, 2, Costo_De_Ventas)
            sheet.write(4, 1, 'RESULTADO BRUTO', bold)
            sheet.write(4, 2, r1)
            sheet.write(6, 0, '5-200-001')
            sheet.write(7, 0, '5-200-002')
            sheet.write(8, 0, '5-200-003')
            sheet.write(9, 0, '5-300')
            sheet.write(6, 1, 'GASTOS DE ADMINISTRACION')
            sheet.write(6, 2, gastos_de_administracion)
            sheet.write(7, 1, 'GASTOS DE OPERACIÓN')
            sheet.write(7, 2,gastos_de_operacion)
            sheet.write(8, 1, 'GASTOS SISTEMAS')
            sheet.write(8, 2, gastos_sistemas)
            sheet.write(9, 1, 'GASTOS DE VENTAS')
            sheet.write(9, 2, gastos_de_ventas)
            sheet.write(10, 1, 'TOTAL GASTOS DE OPERACIÓN')
            sheet.write(10, 2, r2)
            sheet.write(11, 1, 'RESULTADO DE OPERACIÓN', bold)
            sheet.write(11, 2, r3)
            sheet.write(14, 0, '4-300')
            sheet.write(15, 0, '5-400')
            sheet.write(14, 1, 'PRODUCTOS FINANCIEROS')
            sheet.write(14, 2, productos_financieros)
            sheet.write(15, 1, 'GASTOS FINANCIEROS')
            sheet.write(15, 2, gastos_financieros)
            sheet.write(16, 1, 'TOTAL RIF', bold)
            sheet.write(16, 2, r4)
            sheet.write(18, 0, '4-400', bold)
            sheet.write(19, 0, '5-500', bold)
            sheet.write(18, 1, 'OTROS INGRESOS')
            sheet.write(18, 2, otros_ingresos)
            sheet.write(19, 1, 'OTROS GASTOS')
            sheet.write(19, 2,otros_gastos)
            sheet.write(20, 1, 'RESULTADO ANTES DE IMPUESTOS', bold)
            sheet.write(20, 2, r5)
            sheet.write(21, 1, 'RESULTADO', bold)
            sheet.write(21, 2, r6)


        if self.env.cr.dbname=='FERREXTOOL':
            financial_reports=self.env['financial_reports.detail']
            print(self)
            #Ferrextool
            Ventas_f=financial_reports.result_by_account_group('4-100',record.start_date,record.end_date)
            Devoluciones_y_Descuentos_sobre_ventas_F=financial_reports.result_by_account_group('4-200',record.start_date,record.end_date)

            Inventario_Inicial_F=financial_reports.get_initial_balance('1-180',record.start_date,record.end_date)
            Compras=financial_reports.result_by_account_group('1-180',record.start_date,record.end_date,'debit')
            Fletes_de_Compras=financial_reports.result_by_account_group('5-200-022',record.start_date,record.end_date)
            Inventario_Final=financial_reports.get_initial_balance('1-180',record.start_date,record.end_date)-financial_reports.result_by_account_group('1-180',record.start_date,record.end_date)


            Gastos_de_Operacion_F=financial_reports.result_by_account_group('5-200',record.start_date,record.end_date)


            Ingresos_Financieros=financial_reports.result_by_account_group('4-300',record.start_date,record.end_date)
            Otros_Ingresos=financial_reports.result_by_account_group('4-400',record.start_date,record.end_date)
            Gastos_Financieros=financial_reports.result_by_account_group('5-300',record.start_date,record.end_date)
            Otros_Gastos=financial_reports.result_by_account_group('5-400',record.start_date,record.end_date)


            r1_c=Ventas_f+Devoluciones_y_Descuentos_sobre_ventas_F
            r2_c=Inventario_Inicial_F+Compras+Fletes_de_Compras-Inventario_Final
            r3_c=r1_c-r2_c
            r4_c=r3_c-Gastos_de_Operacion_F
            #R4 + INGRESOS FINANCIEROS + OTROS INGRESOS - GASTOS FINANCIEROS - OTROS GASTOS = R5
            r5=r4_c+Ingresos_Financieros+Otros_Ingresos-Gastos_Financieros-Otros_Gastos
    
            sheet = workbook.add_worksheet('ESTADO DE PÉRDIDAS Y GANANCIAS')
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, 'CUENTA AGRUPADORA', bold)
            sheet.write(0, 1, 'CONCEPTO', bold)
            sheet.write(0, 2, 'BALANCE', bold)   
            data=[]
            data.append(('4-100','VENTAS',Ventas_f))
            data.append(('4-200','DEVOLUCIONES Y REBAJAS SOBRE VENTAS',Devoluciones_y_Descuentos_sobre_ventas_F))
            data.append(('','VENTAS NETAS',r1_c))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('1-180','INVENTARIO INICIAL',Inventario_Inicial_F))
            data.append(('1-180','COMPRAS',Compras))
            data.append(('5-200-022','FLETES DE COMPRAS',Fletes_de_Compras))
            data.append(('','COSTO DE VENTAS',r2_c))
            data.append(('','UTILIDAD BRUTA',r3_c))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('5-200','GASTOS DE OPERACIÓN',Gastos_de_Operacion_F))
            data.append(('','UTILIDAD OPERATIVA',r4_c))
            data.append(('','',''))
            data.append(('','',''))
            data.append(('4-300','INGRESOS FINANCIEROS',Ingresos_Financieros))
            data.append(('4-400','OTROS INGRESOS',Otros_Ingresos))
            data.append(('5-300','GASTOS FINANCIEROS',Gastos_Financieros))
            data.append(('5-400','OTROS GASTOS',Otros_Gastos))
            data.append(('','UTILIDAD ANTES DE IMPUESTOS',r5))
            #row col
            for row in range(len(data)):
                for col in range(len(data[row])):
                    print(data[row][col])
                    sheet.write(row+1, col, data[row][col])


       






