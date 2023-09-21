from odoo import _, api, fields, models
import pandas as pd
import io
import calendar

class TrialBalanceReport(models.TransientModel):
    _inherit = 'trial.balance.report.wizard.contabilidad.cfdi'

    report_type = fields.Selection(string='Tipo de Reporte', selection=[('balanza', 'Balanza de Comprobación'),('custom', 'Busqueda Personalizada'), ('reporte', 'Estado de Situación Financiera Y Estado de Pérdidas y Ganancias')])
    
    def generar_reporte_perdidas_y_ganancias_y_estado_financiero(self):
        return self.env.ref('contabilidad_cfdi.situacion_financiera').report_action(self, data={}, config=False)
    
    def dfs_list_edo_perdidas_y_ganancias(self,model,data_for_report_as_data_frame):          
        r1=model.compute_r1(data_for_report_as_data_frame)
        r2=model.compute_r2(data_for_report_as_data_frame,r1[1])
        r3=model.compute_r3(data_for_report_as_data_frame)
        r4=model.compute_r4(data_for_report_as_data_frame)
        r5=model.compute_r5(r2[1],r3[1],r4[1])
        
        return [r1[0],r2[0],r3[0],r4[0],r5[0],r5[1]]



    def dfs_list_edo_de_situacion_financiera(self,model,resultado_del_ejercio_anterior,data_for_report_as_data_frame):                    
        # list of dataframes
        return [model.compute_total_activo_circulante(data_for_report_as_data_frame),model.compute_total_activo_no_circulante(data_for_report_as_data_frame),model.compute_total_pasivo(data_for_report_as_data_frame),model.compute_total_capital_contable(data_for_report_as_data_frame,resultado_del_ejercio_anterior)]

    def financial_reports_prepare_report_trial_balance(self,model,month):
        model.ensure_one()
        return {
            'date_from': model.year+'-'+month+'-01',
            'date_to': model.year+'-'+month+'-'+str(calendar.monthrange(int(model.year),int(month))[1]),
            'only_posted_moves': model.target_move == 'posted',
            'hide_account_at_0': model.hide_account_at_0,
            'foreign_currency': model.foreign_currency,
            'company_id': model.company_id.id,
            'filter_account_ids': [(6, 0, model.account_ids.ids)],
            'filter_partner_ids': [(6, 0, model.partner_ids.ids)],
            'filter_journal_ids': [(6, 0, model.journal_ids.ids)],
            'fy_start_date': model.fy_start_date,
            'hierarchy_on': model.hierarchy_on,
            'limit_hierarchy_level': model.limit_hierarchy_level,
            'show_hierarchy_level': model.show_hierarchy_level,
            'show_partner_details': model.show_partner_details,
            'contabilidad_electronica':True,
        }
        
    def generate_data_for_report_as_data_frame(self,trial_balancer_report,dict_prepare_report_trial_balance):
        model = trial_balancer_report.env['report_trial_balance_contabilidad_cfdi']
        print(dict_prepare_report_trial_balance)
        report = model.create(dict_prepare_report_trial_balance)
        context= {'active_model': 'report_trial_balance_contabilidad_cfdi', 'is_cuentas_de_orden': True, 'is_contabilidad_electronica': True}
        report.with_context(context).compute_data_for_report()
        trial_balancer_report._cr.execute("SELECT * FROM report_trial_balance_account_contabilidad_cfdi where report_id = "+str(report.id))
        computed_data = trial_balancer_report.env.cr.dictfetchall()                        
        return pd.DataFrame(computed_data)


    def get_account_name(self,account_id):
        return self.env['account.group'].browse(int(account_id)).name or 'N/A'
    
    def sum_final_balance(self,df):
        return df['final_balance'].sum()
        
    def get_account_group_ids(self,ARRAY_GROUP_CODE_PREFIX):
        return self.env['account.group'].search([('code_prefix','in',ARRAY_GROUP_CODE_PREFIX)]).ids
    
    def get_group_code_prefix(self,account_id):
        return self.env['account.group'].browse(int(account_id)).code_prefix

    def get_account_account_code_prefix(self,account_id):
        return self.env['account.account'].browse(int(account_id)).code 

    def get_account_account_name(self,account_id):
        return self.env['account.account'].browse(int(account_id)).name or 'N/A'
    
    def generate_data_frame_for_acoount_group(self,ARRAY_GROUP_CODE_PREFIX,df):
        account_group = self.env['account.group'].search([('code_prefix','in',ARRAY_GROUP_CODE_PREFIX)]).ids
        df=df[df.account_group_id.isin(account_group)]
        df['group_code_prefix']=df['account_group_id'].apply(self.get_group_code_prefix)   
        df['group_name']=df['account_group_id'].apply(self.get_account_name)        
        df['result_d_c_'] = df['final_balance'] - df['initial_balance']                
        return (df[['group_code_prefix','name','final_balance','result_d_c_']])

    def generate_data_frame_for_account_account(self,ARRAY_ACCOUNT_CODE_PREFIX,df):
        accounts = self.env['account.account'].search([('code','in',ARRAY_ACCOUNT_CODE_PREFIX)]).ids
        df=df[df.account_id.isin(accounts)]
        df['group_code_prefix']=df['account_id'].apply(self.get_account_account_code_prefix)
        df['group_name']=df['account_id'].apply(self.get_account_account_name)
        df['result_d_c_'] = df['final_balance'] - df['initial_balance']        
        return (df[['group_code_prefix','name','final_balance','result_d_c_']])

    def compute_total_activo_circulante(self,df):
        ACTIVO=["1-110","1-120","1-130","1-140","1-160","1-180","1-190","1-200","1-210","1-220","1-230-001"]
        df_activo_cirlulante =self.generate_data_frame_for_acoount_group(ACTIVO,df)
        new_row_name = pd.DataFrame({'name':['TOTAL ACTIVO CIRCULANTE'],'group_code_prefix':["-"],'final_balance':[0]})
        df_activo_cirlulante=pd.concat([new_row_name, df_activo_cirlulante]).reset_index(drop = True)
        total_activo_cirlulante=self.sum_final_balance(df_activo_cirlulante)        
        new_row = {'name':'TOTAL ACTIVO CIRCULANTE', 'group_code_prefix':"-", 'final_balance':total_activo_cirlulante}
        df_activo_cirlulante=df_activo_cirlulante.append(new_row,ignore_index=True)
        return df_activo_cirlulante
    
    def compute_total_activo_no_circulante(self,df):
        ACTIVO_NO_CIRCULANTE=["1-300-001","1-300-003-001","1-300-003-002","1-300-002-001","1-300-002-002","1-300-006-001","1-300-006-002","1-300-004-001","1-300-004-002","1-300-005-001","1-300-005-002","1-300-008-001","1-300-007-001","1-300-007-002","1-300-009-001","1-300-009-002"]
        df_activo_no_cirlulante =self.generate_data_frame_for_account_account(ACTIVO_NO_CIRCULANTE,df)
        new_row_name = pd.DataFrame({'name':['ACTIVO NO CIRCULANTE'],'group_code_prefix':["-"],'final_balance':[0]})
        df_activo_no_cirlulante=pd.concat([new_row_name, df_activo_no_cirlulante]).reset_index(drop = True)
        total_activo_no_cirlulante=self.sum_final_balance(df_activo_no_cirlulante)
        new_row = {'name':'TOTAL ACTIVO NO CIRCULANTE', 'group_code_prefix':"-", 'final_balance':total_activo_no_cirlulante}
        df_activo_no_cirlulante=df_activo_no_cirlulante.append(new_row,ignore_index=True)
        return df_activo_no_cirlulante
    
    def compute_total_pasivo(self,df):
        PASIVO_A_CORTO_PLAZO=["2-100","2-120","2-130","2-135","2-140","2-150","2-160","2-165"]
        df_pasivo =self.generate_data_frame_for_acoount_group(PASIVO_A_CORTO_PLAZO,df)
        new_row_name = pd.DataFrame({'name':['PASIVO A CORTO PLAZO'],'group_code_prefix':["-"],'final_balance':[0]})
        df_pasivo=pd.concat([new_row_name, df_pasivo]).reset_index(drop = True)
        total_pasivo=self.sum_final_balance(df_pasivo)
        new_row = {'name':'TOTAL PASIVO A CORTO PLAZO', 'group_code_prefix':"-", 'final_balance':total_pasivo}
        df_pasivo=df_pasivo.append(new_row,ignore_index=True)
        return df_pasivo
        
    def compute_total_capital_contable(self,df,resultado_de_ejercicio_anterior):
        CAPITAL_CONTABLE = ["3-100","3-300","3-400"]
        df_capital_contable =self.generate_data_frame_for_acoount_group(CAPITAL_CONTABLE,df)
        new_row_name = pd.DataFrame({'name':['CAPITAL CONTABLE'],'group_code_prefix':["-"],'final_balance':[0]})
        df_capital_contable=pd.concat([new_row_name, df_capital_contable]).reset_index(drop = True)
        new_row = {'name':'RESULTADO DEL EJERCICIO  ', 'group_code_prefix':"-", 'final_balance':resultado_de_ejercicio_anterior}
        df_capital_contable=df_capital_contable.append(new_row,ignore_index=True)
        total_capital_contable=self.sum_final_balance(df_capital_contable)
        new_row = {'name':'TOTAL CAPITAL CONTABLE', 'group_code_prefix':"-", 'final_balance':total_capital_contable}
        df_capital_contable=df_capital_contable.append(new_row,ignore_index=True)
        return df_capital_contable

    
###ESTADO DE PERDIDAS Y GANANCIAS
    def compute_r1(self,df):

        R1=['4-100','4-200']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        df_ventas_netas=df_r1[df_r1['group_code_prefix']=='4-100']
        ventas_netas=df_ventas_netas['result_d_c_']._values[0]
        df_costo_de_ventas=df_r1[df_r1['group_code_prefix']=='4-200']
        costo_de_ventas=df_costo_de_ventas['result_d_c_']._values[0]
        new_row = {'name':'TOTAL INGRESOS (R1)', 'group_code_prefix':"VENTAS - DESCUENTOS Y DEV SOBRE VENTAS = R1", 'result_d_c_':ventas_netas-costo_de_ventas}
        df_r1=df_r1.append(new_row,ignore_index=True)
        return (df_r1,ventas_netas-costo_de_ventas)
        
        
    def compute_r2(self,df,R1_result):
        R2=['5-200']
        df_r2 =self.generate_data_frame_for_acoount_group(R2,df)
        df_gastos_de_administracion=df_r2[df_r2['group_code_prefix']=='5-200']
        gastos_de_administracion=df_gastos_de_administracion['result_d_c_']._values[0]            
        new_row = {'name':'RESULTADOS DE LA OPERACIÓN (R2)', 'group_code_prefix':"Ʃ GASTOS = R2", 'result_d_c_':R1_result-gastos_de_administracion}
        df_r2=df_r2.append(new_row,ignore_index=True)        
        return (df_r2,R1_result-R1_result-gastos_de_administracion)
        
        
    def compute_r3(self,df):
        R2=['5-400-001','5-400-002','5-400-004']
        df_r2 =self.generate_data_frame_for_account_account(R2,df)
        total_gastos_de_operacion=self.sum_final_balance(df_r2)
        print(df_r2)
        new_row = {'name':'RESULTADO DE OPERACIÓN (R3)', 'group_code_prefix':"R1 - R2 = R3", 'result_d_c_':total_gastos_de_operacion}
        df_r2=df_r2.append(new_row,ignore_index=True)        
        return (df_r2,total_gastos_de_operacion)


    def compute_r4(self,df):
        R4=['4-300','5-400']
        df_r4 =self.generate_data_frame_for_acoount_group(R4,df)
        df_productos_financieros=df_r4[df_r4['group_code_prefix']=='4-300']
        productos_financieros=df_productos_financieros['result_d_c_']._values[0]        
        df_gastos_financieros=df_r4[df_r4['group_code_prefix']=='5-400']
        gastos_financieros=df_gastos_financieros['result_d_c_']._values[0]
        new_row = {'name':'TOTAL RIF (R4)', 'group_code_prefix':"PF - GF = R4", 'result_d_c_':productos_financieros-gastos_financieros}
        df_r4=df_r4.append(new_row,ignore_index=True)        
        return (df_r4,productos_financieros-gastos_financieros)
        



    def compute_r5(self,R2_result,R3_result,R4_result):
        df = pd.DataFrame()
        new_row = {'name':'RESULTADO ANTES DE IMPUESTOS', 'group_code_prefix':"R3 + R4 + R5 = R6", 'result_d_c_':R2_result+R3_result+R4_result}
        df=df.append(new_row,ignore_index=True)
        return (df,R2_result+R3_result+R4_result)
        
    def costo_de_ventas(self,data_for_report_as_data_frame):
        print(data_for_report_as_data_frame)

        


            