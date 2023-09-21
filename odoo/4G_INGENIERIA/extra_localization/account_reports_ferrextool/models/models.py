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
        r2_3=model.compute_r2_r3(data_for_report_as_data_frame,r1[1])
        r4=model.compute_r4(data_for_report_as_data_frame,r2_3[1])
        r5=model.compute_r5(data_for_report_as_data_frame,r4[1])
        return [r1[0],r2_3[0],r4[0],r5[0]]



    def dfs_list_edo_de_situacion_financiera(self,model,resultado_del_ejercio_anterior,data_for_report_as_data_frame):                    
        # list of dataframes
        x=model.compute_total_activo_circulante(data_for_report_as_data_frame)
        y=model.compute_total_activo_fijo(data_for_report_as_data_frame)
        d=model.compute_total_pasivo(data_for_report_as_data_frame)
        p=model.compute_total_capital_contable(data_for_report_as_data_frame,resultado_del_ejercio_anterior)
        return [model.compute_total_activo_circulante(data_for_report_as_data_frame),model.compute_total_activo_fijo(data_for_report_as_data_frame),model.compute_total_pasivo(data_for_report_as_data_frame),model.compute_total_capital_contable(data_for_report_as_data_frame,resultado_del_ejercio_anterior)]

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
        print(df)         
        return (df[['group_code_prefix','name','final_balance','result_d_c_','initial_balance','debit']])

    def generate_data_frame_for_account_account(self,ARRAY_ACCOUNT_CODE_PREFIX,df):
        accounts = self.env['account.account'].search([('code','in',ARRAY_ACCOUNT_CODE_PREFIX)]).ids
        df=df[df.account_id.isin(accounts)]
        df['result_d_c_'] = df['final_balance']-df['initial_balance']
        df['group_code_prefix']=df['account_id'].apply(self.get_account_account_code_prefix)
        df['group_name']=df['account_id'].apply(self.get_account_account_name)
        df['debit']=df['debit']   
        df['credit']=df['credit']    
        df['final_balance']=df['final_balance']  
        df['initial_balance']=df['initial_balance']
        df['debit-credit']=df['debit']-df['credit']   
        print(df[['group_code_prefix','name','result_d_c_','debit','credit','debit-credit','initial_balance','final_balance']]) 
        return (df[['group_code_prefix','name','result_d_c_','debit','credit','debit-credit','initial_balance','final_balance']])


    def compute_total_activo_circulante(self,df):
        ACTIVO=['1-110','1-120','1-130','1-170','1-180','1-190','1-200','1-220','1-230']
        df_activo_cirlulante =self.generate_data_frame_for_acoount_group(ACTIVO,df)
        new_row_name = pd.DataFrame({'name':['TOTAL ACTIVO CIRCULANTE'],'group_code_prefix':["-"],'final_balance':[0]})
        df_activo_cirlulante=pd.concat([new_row_name, df_activo_cirlulante]).reset_index(drop = True)
        total_activo_cirlulante=self.sum_final_balance(df_activo_cirlulante)        
        new_row = {'name':'TOTAL ACTIVO CIRCULANTE', 'group_code_prefix':"-", 'final_balance':total_activo_cirlulante}
        df_activo_cirlulante=df_activo_cirlulante.append(new_row,ignore_index=True)
        return df_activo_cirlulante


    #Activo Fijo
    def compute_total_activo_fijo(self,df):
        ACTIVO_FIJO=['1-310-001','1-310-002','1-320-001','1-320-002']
        df_activo_fijo =self.generate_data_frame_for_account_account(ACTIVO_FIJO,df)
        new_row_name = pd.DataFrame({'name':['ACTIVO FIJO'],'group_code_prefix':["-"],'final_balance':[0]})
        df_activo_fijo=pd.concat([new_row_name, df_activo_fijo]).reset_index(drop = True)
        total_activo_fijo=self.sum_final_balance(df_activo_fijo)
        new_row = {'name':'TOTAL FIJO', 'group_code_prefix':"-", 'final_balance':total_activo_fijo}
        df_activo_fijo=df_activo_fijo.append(new_row,ignore_index=True)
        return df_activo_fijo


    def compute_total_pasivo(self,df):
        PASIVO_A_CORTO_PLAZO=['2-100-001','2-110','2-130','2-140','2-150','2-160','2-170','2-180','2-190']
        df_pasivo =self.generate_data_frame_for_acoount_group(PASIVO_A_CORTO_PLAZO,df)
        new_row_name = pd.DataFrame({'name':['PASIVO A CORTO PLAZO'],'group_code_prefix':["-"],'final_balance':[0]})
        df_pasivo=pd.concat([new_row_name, df_pasivo]).reset_index(drop = True)
        total_pasivo=self.sum_final_balance(df_pasivo)
        new_row = {'name':'TOTAL PASIVO A CORTO PLAZO', 'group_code_prefix':"-", 'final_balance':total_pasivo}
        df_pasivo=df_pasivo.append(new_row,ignore_index=True)
        return df_pasivo
        
    def compute_total_capital_contable(self,df,resultado_de_ejercicio_anterior):
        CAPITAL_CONTABLE = ["3-100","3-400"]
        df_capital_contable =self.generate_data_frame_for_acoount_group(CAPITAL_CONTABLE,df)
        new_row_name = pd.DataFrame({'name':['CAPITAL SOCIAL'],'group_code_prefix':["-"],'final_balance':[0]})
        df_capital_contable=pd.concat([new_row_name, df_capital_contable]).reset_index(drop = True)
        print(resultado_de_ejercicio_anterior)
        new_row = {'name':'RESULTADO DEL EJERCICIO  ', 'group_code_prefix':"-", 'final_balance':resultado_de_ejercicio_anterior}
        df_capital_contable=df_capital_contable.append(new_row,ignore_index=True)
        total_capital_contable=self.sum_final_balance(df_capital_contable)
        new_row = {'name':'TOTAL CAPITAL SOCIAL', 'group_code_prefix':"-", 'final_balance':total_capital_contable}
        df_capital_contable=df_capital_contable.append(new_row,ignore_index=True)
        return df_capital_contable

    
    
    
    
    
###ESTADO DE PERDIDAS Y GANANCIAS
    def compute_r1(self,df):
        R1=['4-100','4-200']        
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        df_ventas_netas=df_r1[df_r1['group_code_prefix']=='4-100']
        ventas=df_ventas_netas['result_d_c_']._values[0]
        df_devoluciones_y_rebajas_sobre_ventas=df_r1[df_r1['group_code_prefix']=='4-200']
        devoluciones_y_rebajas_sobre_ventas=df_devoluciones_y_rebajas_sobre_ventas['result_d_c_']._values[0]
        new_row = {'name':'VENTAS - DEV SOBRE VENTAS = R1', 'group_code_prefix':"VENTAS NETAS (R1)", 'result_d_c_':ventas-devoluciones_y_rebajas_sobre_ventas}
        df_r1=df_r1.append(new_row,ignore_index=True)
        return (df_r1,ventas-devoluciones_y_rebajas_sobre_ventas)
        
        
    def compute_r2_r3(self,df,R1_result):
        R2=['1-180','5-200-022']
        df_r2 =self.generate_data_frame_for_acoount_group(['1-180'],df)
        #total_gastos_de_operacion=self.sum_final_balance(df_r2)

        df_inventario_inicial=df_r2[df_r2['group_code_prefix']=='1-180']
        print(df_inventario_inicial)
        inventario_inicial=df_inventario_inicial['initial_balance']._values[0]
        inventario_final=df_inventario_inicial['final_balance']._values[0]
        compras=df_inventario_inicial['debit']._values[0]
        
        
        df_r3 =self.generate_data_frame_for_account_account(['5-200-022'],df)
        print(df_r3)
        df_fletes=df_r3[df_r3['group_code_prefix']=='5-200-022']
        print(df_fletes)
        fletes_ini=df_fletes['initial_balance']._values[0]
        flete_final=df_fletes['final_balance']._values[0]
        
        
        
        new_df = pd.DataFrame()                
        new_row = {'name':'INVENTARIO INICIAL', 'group_code_prefix':"1-180", 'result_d_c_':inventario_inicial}
        new_df=new_df.append(new_row,ignore_index=True)        
        new_row = {'name':'COMPRAS', 'group_code_prefix':"1-180", 'result_d_c_':compras}
        new_df=new_df.append(new_row,ignore_index=True)        
        new_row = {'name':'FLETES DE COMPRAS', 'group_code_prefix':"5-200-022", 'result_d_c_':flete_final-fletes_ini}
        new_df=new_df.append(new_row,ignore_index=True)        
        new_row = {'name':'INVENTARIO FINAL', 'group_code_prefix':"1-180", 'result_d_c_':inventario_final}
        new_df=new_df.append(new_row,ignore_index=True)
        
        
        new_row = {'name':'INVENTARIO INICIAL + COMPRAS + FLETES - INVENTARIO FINAL  =  R2', 'group_code_prefix':"COSTOS DE VENTAS (R2)", 'result_d_c_':inventario_inicial+compras+(flete_final-fletes_ini)-inventario_final}
        new_df=new_df.append(new_row,ignore_index=True)
        
        
        new_row = {'name':'R1 - R2 = R3', 'group_code_prefix':"UTILIDAD BRUTA (R3)", 'result_d_c_':R1_result-(inventario_inicial+compras+(flete_final-fletes_ini)-inventario_final)}
        new_df=new_df.append(new_row,ignore_index=True)   
        
        return (new_df,R1_result-(inventario_inicial+compras+(flete_final-fletes_ini)-inventario_final))
        



    def compute_r4(self,df,R3):
        R4=['5-200']
        df_r4 =self.generate_data_frame_for_acoount_group(R4,df)
        df_gastos_de_operacion=df_r4[df_r4['group_code_prefix']=='5-200']
        gastos_de_operacion_final=df_gastos_de_operacion['final_balance']._values[0]
        gastos_de_operacion_inicial=df_gastos_de_operacion['initial_balance']._values[0]
        new_row = {'name':'R3 - GASTOS DE OPERACIÓN = R4', 'group_code_prefix':"UTILIDAD OPERATIVA (R4)", 'result_d_c_': R3-gastos_de_operacion_final-gastos_de_operacion_inicial}
        df_r4=df_r4.append(new_row,ignore_index=True)        
        return (df_r4,R3-gastos_de_operacion_final-gastos_de_operacion_inicial)
        

    def compute_r5(self,df,R4):
        R5=['4-300','4-400','5-300','5-400']
        df_r5 = self.generate_data_frame_for_acoount_group(R5,df)

        df_ingresos_financieros=df_r5[df_r5['group_code_prefix']=='4-300']
        ingresos_financieros=df_ingresos_financieros['result_d_c_']._values[0]   

        df_otros_ingresos=df_r5[df_r5['group_code_prefix']=='4-400']
        otros_ingresos=df_otros_ingresos['result_d_c_']._values[0]
             
        df_gastos_financieros=df_r5[df_r5['group_code_prefix']=='5-300']
        gastos_financieros=df_gastos_financieros['result_d_c_']._values[0]
        
        df_otros_gastos=df_r5[df_r5['group_code_prefix']=='5-400']
        otros_gastos=df_otros_gastos['result_d_c_']._values[0]
        
        
        new_row = {'name':'R4 + INGRESOS FINANCIEROS + OTROS INGRESOS - GASTOS FINANCIEROS - OTROS GASTOS = R5', 'group_code_prefix':"UTILIDAD ANTES DE IMPUESTOS (R5)", 'result_d_c_':R4+ingresos_financieros+otros_ingresos-gastos_financieros-otros_gastos}
        df_r5=df_r5.append(new_row,ignore_index=True)
        return (df_r5,R4+ingresos_financieros+otros_ingresos-gastos_financieros-otros_gastos)

        
##############################Costo de Ventas#######################

    def costo_de_ventas(self,costo_de_ventas_obj):
        dict_prepare_report_trial_balance={
        'date_from': costo_de_ventas_obj.ano+'-'+costo_de_ventas_obj.mes+'-01',
        'date_to': costo_de_ventas_obj.ano+'-'+costo_de_ventas_obj.mes+'-'+str(calendar.monthrange(int(costo_de_ventas_obj.ano),int(costo_de_ventas_obj.mes))[1]),
        'only_posted_moves': False, 
        'hide_account_at_0': True, 
        'foreign_currency': False, 
        'company_id': 1, 
        'filter_account_ids': [(6, 0, [])], 
        'filter_partner_ids': [(6, 0, [])], 
        'filter_journal_ids': [(6, 0, [])], 
        'fy_start_date': costo_de_ventas_obj.ano+'-'+'01'+'-01', 
        'hierarchy_on': 'computed', 
        'limit_hierarchy_level': False, 
        'show_hierarchy_level': 1, 
        'show_partner_details': False, 
        'contabilidad_electronica': True
        }
        costo_de_ventas_vista_line=self.env['costo_de_ventas.line']
        trial_balance_report=self.env['trial.balance.report.wizard.contabilidad.cfdi']        
        data_for_report_as_data_frame = trial_balance_report.generate_data_for_report_as_data_frame(self,dict_prepare_report_trial_balance)
        inventario_incial=self.inventario_incial(data_for_report_as_data_frame)
        compras=self.compras(data_for_report_as_data_frame)
        fletes=self.fletes(data_for_report_as_data_frame)
        inventario_final=self.inventario_final(data_for_report_as_data_frame)
        total=inventario_incial+compras+fletes-inventario_final
        print(total)
        costo_de_ventas_obj.total=inventario_incial+compras+fletes-inventario_final
        costo_de_ventas_vista_line.create({'cdv_vista_id':costo_de_ventas_obj.id,'concepto':'INVENTARIO INICIAL','importe':inventario_incial,'tipo':'inventario'})
        costo_de_ventas_vista_line.create({'cdv_vista_id':costo_de_ventas_obj.id,'concepto':'COMPRAS','importe':compras,'tipo':'compras'})
        costo_de_ventas_vista_line.create({'cdv_vista_id':costo_de_ventas_obj.id,'concepto':'FLETES DE COMPRAS','importe':fletes,'tipo':'fletes'})
        costo_de_ventas_vista_line.create({'cdv_vista_id':costo_de_ventas_obj.id,'concepto':'INVENTARIO FINAL','importe':inventario_final,'tipo':'inventario_f'})
        

    def inventario_incial(self,df):
        #Material Consumido
        R1=['1-180']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        data_frame=df_r1[df_r1['group_code_prefix']=='1-180']
        #result_d_c_  movimientos del mes
        balance_inicial=float(data_frame['initial_balance']._values[0])
        return balance_inicial

    def compras(self,df):
        #Material Consumido
        R1=['1-180']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        data_frame=df_r1[df_r1['group_code_prefix']=='1-180']
        #result_d_c_  movimientos del mes
        compras=float(data_frame['debit']._values[0])
        return compras

    def inventario_final(self,df):
        #Material Consumido
        R1=['1-180']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        data_frame=df_r1[df_r1['group_code_prefix']=='1-180']
        #result_d_c_  movimientos del mes
        compras=float(data_frame['final_balance']._values[0])
        return compras


    def fletes(self,df):
        R1=['5-200-022']
        df_r1 = self.generate_data_frame_for_account_account(R1,df)
        result=df_r1['debit-credit'].sum()       
        return result

    
        


            