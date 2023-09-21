from odoo import _, api, fields, models
import pandas as pd
import io


class SituacionFinancieraXlsxReport(models.AbstractModel):
    
    _name = 'report.contabilidad_cfdi.pt_report'
    _inherit = 'report.report_xlsx.abstract'

    def total_facturas_con_iva(self,start_date,end_date):
        total_facturas_iva=0
        #facturas_con_iva=self.env['account.invoice'].search([('type','=','out_invoice'),('state','in',['open','paid']),('amount_untaxed_signed','>',0),('date_invoice','>=',),('date_invoice','<=',end_date)])
        facturas_con_iva=self.env['account.invoice'].search([('type','=','out_invoice'),('state','not in',['draft','cancel']),('amount_untaxed_signed','>',0),('amount_tax','>',0),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        for factura in facturas_con_iva:
            total_facturas_iva=total_facturas_iva+factura.amount_untaxed_signed
        return total_facturas_iva
        
    def total_facturas_sin_iva(self,start_date,end_date):
        facturas_sin_iva=self.env['account.invoice'].search([('type','=','out_invoice'),('state','not in',['draft','cancel']),('amount_tax','<=',0),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        total_facturas_sin_iva=0
        for factura in facturas_sin_iva:
            total_facturas_sin_iva=total_facturas_sin_iva+factura.amount_untaxed_signed
        return total_facturas_sin_iva

    def total_notas_de_credito_con_iva(self,start_date,end_date):
        total_notas_de_credito_iva=0
        notas_de_credito_iva=self.env['account.invoice'].search([('type','=','out_refund'),('amount_tax','!=',0),('state','not in',['draft','cancel']),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        for nota_iva in notas_de_credito_iva:
            total_notas_de_credito_iva=total_notas_de_credito_iva+nota_iva.amount_untaxed_signed
        return total_notas_de_credito_iva

    def total_notas_de_credito_sin_iva(self,start_date,end_date):
        total_notas_de_credito_sin_iva=0
        notas_de_credito_sin_iva=self.env['account.invoice'].search([('type','=','out_refund'),('amount_tax','=',0),('state','not in',['draft','cancel']),('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
        for nota_iva in notas_de_credito_sin_iva:
            total_notas_de_credito_sin_iva=total_notas_de_credito_sin_iva+nota_iva.amount_untaxed_signed
        return total_notas_de_credito_sin_iva
    
    def get_list_of_restant_years(self,model):
        month=int(model.month)
        months_arr=[]
        for item in range(month):
            months_arr.append(str(item+1))
        return months_arr  
    
    def get_df_pt(self,ingresos_nominales_acumulados,month,model,coeficiente_de_utilidad,factor_de_calculo_isr,isr_causado_acumulado_anterior):                    
            trial_balance_report=self.env['trial.balance.report.wizard.contabilidad.cfdi']
            dict_prepare_report_trial_balance=trial_balance_report.financial_reports_prepare_report_trial_balance_pt(model,month)
            data_for_report_as_data_frame = trial_balance_report.generate_data_for_report_as_data_frame_pt(model,dict_prepare_report_trial_balance)        
            df_acc=trial_balance_report.generate_data_frame_for_account_account_pt(dict_prepare_report_trial_balance.get('filter_account_ids')[0][2],data_for_report_as_data_frame)          
            df_acc=df_acc.append({'name':'-', 'movimientos_del_mes':0, 'account_code':'---------'},ignore_index=True)
            df_acc=df_acc.append({'name':'Facturas Con Iva', 'movimientos_del_mes':self.total_facturas_con_iva(dict_prepare_report_trial_balance.get('date_from'),dict_prepare_report_trial_balance.get('date_to')), 'account_code':'---------'},ignore_index=True)
            df_acc=df_acc.append({'name':'Facturas Sin Iva', 'movimientos_del_mes':self.total_facturas_sin_iva(dict_prepare_report_trial_balance.get('date_from'),dict_prepare_report_trial_balance.get('date_to')), 'account_code':'---------'},ignore_index=True)
            df_acc=df_acc.append({'name':'Notas de Crédito Con Iva', 'movimientos_del_mes':self.total_notas_de_credito_con_iva(dict_prepare_report_trial_balance.get('date_from'),dict_prepare_report_trial_balance.get('date_to')), 'account_code':'---------'},ignore_index=True)
            df_acc=df_acc.append({'name':'Notas de Crédito Sin Iva', 'movimientos_del_mes':self.total_notas_de_credito_sin_iva(dict_prepare_report_trial_balance.get('date_from'),dict_prepare_report_trial_balance.get('date_to')), 'account_code':'---------'},ignore_index=True)
            df_acc=df_acc.append({'name':'-', 'movimientos_del_mes':0, 'account_code':'---------'},ignore_index=True)
            movimientos_del_mes=trial_balance_report.sum_movimientos_del_mes(df_acc)
            df_acc=df_acc.append({'name':'TOTAL INGRESOS NOMINALES', 'movimientos_del_mes':movimientos_del_mes , 'account_code':'---------'},ignore_index=True)                        
            ingresos_nominales_acumulados = ingresos_nominales_acumulados+movimientos_del_mes
            df_acc=df_acc.append({'name':'TOTAL INGRESOS NOMINALES ACUMULADOS', 'movimientos_del_mes':ingresos_nominales_acumulados, 'account_code':'---------'},ignore_index=True)                                                
            df_acc=df_acc.append({'name':'COEFICIENTE DE UTILIDAD', 'movimientos_del_mes':coeficiente_de_utilidad, 'account_code':'C.U'},ignore_index=True)
            utilidad_estimada=ingresos_nominales_acumulados*coeficiente_de_utilidad
            df_acc=df_acc.append({'name':'UTILIDAD ESTIMADA', 'movimientos_del_mes':utilidad_estimada, 'account_code':'U.E'},ignore_index=True)
            isr_causado_acumulado=utilidad_estimada*factor_de_calculo_isr
            df_acc=df_acc.append({'name':'ISR CAUSADO ACUMULADO', 'movimientos_del_mes':isr_causado_acumulado, 'account_code':'---------'},ignore_index=True)
            isr_a_pagar_del_mes=isr_causado_acumulado-isr_causado_acumulado_anterior
            df_acc=df_acc.append({'name':'ISR A PAGAR DEL MES', 'movimientos_del_mes':isr_a_pagar_del_mes, 'account_code':'---------'},ignore_index=True)                                
            return df_acc,ingresos_nominales_acumulados,isr_causado_acumulado
    

    def generate_xlsx_report(self, workbook, data, model):
        
        def get_month_name(number):
            if number=='1':
                return 'ENERO'
            if number=='2':
                return 'FEBRERO'
            if number=='3':
                return 'MARZO'            
            if number=='4':
                return 'ABRIL'
            if number=='5':
                return 'MAYO'
            if number=='6':
                return 'JUNIO'
            if number=='7':
                return 'JULIO'
            if number=='8':
                return 'AGOSTO'
            if number=='9':
                return 'SEPTIEMBRE'                
            if number=='10':
                return 'OCTUBRE'
            if number=='11':
                return 'NOVIEMBRE'
            if number=='12':
                return 'DICIEMBRE'
            
        def write_workbook_horizontally(sheet,arr,walk_row,walk_column): 
            col_ret=0
            row_ret=0                           
            for row in range(len(arr)):
                for column in range(len(arr[row])):
                    row_ret=row_ret+row+walk_row
                    col_ret=col_ret+column+walk_column
                    sheet.write(row+walk_row, column+walk_column,arr[row][column])
            return arr,row_ret,col_ret
        ingresos_nominales_acumulados=0
        isr_causado_acumulado_anterior=0
        coeficiente_de_utilidad=0.0282
        factor_de_calculo_isr=.30
        space=0
        sheet = workbook.add_worksheet('PT')
        
        for month in self.get_list_of_restant_years(model):
            df_result=self.get_df_pt(ingresos_nominales_acumulados,month,model,coeficiente_de_utilidad,factor_de_calculo_isr,isr_causado_acumulado_anterior)
            ingresos_nominales_acumulados=df_result[1]
            isr_causado_acumulado_anterior=df_result[2]
            header = pd.DataFrame({'name':[get_month_name(month)], 'movimientos_del_mes':[int(0000000)], 'account_code':[get_month_name(month)]})
            df_result=pd.concat([header, df_result[0].round(4)]).reset_index(drop = True)            
            pd.set_option('float_format', '{:f}'.format)        
            write_workbook_horizontally(sheet,df_result.to_numpy(),0,space)
            space=space+4
        


        
        