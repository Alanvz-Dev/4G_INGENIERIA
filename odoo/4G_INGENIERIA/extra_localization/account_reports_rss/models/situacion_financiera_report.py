from odoo import _, api, fields, models
import pandas as pd
import io


class SituacionFinancieraXlsxReport(models.AbstractModel):
    
    _name = 'report.contabilidad_cfdi.situacion_financiera_report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, model):
        def get_list_of_restant_years(model):
            month=int(model.month)
            months_arr=[]
            for item in range(month):
                months_arr.append(str(item+1))
            return months_arr
        trial_balance_report=self.env['trial.balance.report.wizard.contabilidad.cfdi']
        df_list=[]
        for month in get_list_of_restant_years(model):            
            dict_prepare_report_trial_balance=trial_balance_report.financial_reports_prepare_report_trial_balance(model,month)
            data_for_report_as_data_frame = trial_balance_report.generate_data_for_report_as_data_frame(model,dict_prepare_report_trial_balance)
            df_trial_balance_report=trial_balance_report.dfs_list_edo_perdidas_y_ganancias(model,data_for_report_as_data_frame)
            #xxx=trial_balance_report.costo_de_ventas(data_for_report_as_data_frame)
            df_list.append(df_trial_balance_report)
        #Dataframe del Mes
        print(data_for_report_as_data_frame)
        print(type(data_for_report_as_data_frame))        
        sheet = workbook.add_worksheet('Estado de Pérdidas y Ganancias')
        print(df_list)
        print(type(df_list))       
        

        def generate_array_from_data_frame(df_list):
            row_count_=0
            arr=[]
            for df0 in df_list:
                arr0=[]
                for df in df0:                            
                    if isinstance(df, pd.DataFrame):          
                        for index, row in df.iterrows():
                            row_count_=row_count_+1
                            arr0.append([row['group_code_prefix'], row['name'],row['result_d_c_']])
                arr.append(arr0)
            return arr
        
        def generate_array_from_data_frame_situacion_financiera(df_list):
            row_count_=0
            arr=[]
            for df0 in df_list:
                arr0=[]
                for df in df0:                            
                    if isinstance(df, pd.DataFrame):          
                        for index, row in df.iterrows():
                            row_count_=row_count_+1
                            arr0.append([row['group_code_prefix'], row['name'],row['final_balance']])
                arr.append(arr0)
            return arr
        
        
        def write_workbook_horizontally(sheet,arr,walk_row,walk_column): 
            col_ret=0
            row_ret=0                           
            for row in range(len(arr)):
                for column in range(len(arr[row])):
                    row_ret=row_ret+row+walk_row
                    col_ret=col_ret+column+walk_column
                    sheet.write(row+walk_row, column+walk_column,arr[row][column])
            return arr,row_ret,col_ret
        
        space=0
        for month in generate_array_from_data_frame(df_list):
            write_workbook_horizontally(sheet,month,0,space)
            space=space+5





        df_list_2=[]
        sheet = workbook.add_worksheet('Estado de Situación Financiera')
        count=0
        for month in get_list_of_restant_years(model):
            print(df_list)           
            dict_prepare_report_trial_balance=trial_balance_report.financial_reports_prepare_report_trial_balance(model,month)
            print(df_list)
            data_for_report_as_data_frame = trial_balance_report.generate_data_for_report_as_data_frame(model,dict_prepare_report_trial_balance)
            print(df_list)
            uo=df_list[count][-1]
            print(uo)
            io=df_list[count]
            print(io)
            df_trial_balance_report= trial_balance_report.dfs_list_edo_de_situacion_financiera(model,df_list[count][-1],data_for_report_as_data_frame)
            df_list_2.append(df_trial_balance_report)
            count=count+1
                        
        space=0
        for month in generate_array_from_data_frame_situacion_financiera(df_list_2):
            write_workbook_horizontally(sheet,month,0,space)
            space=space+5