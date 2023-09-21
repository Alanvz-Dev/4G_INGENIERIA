from odoo import _, api, fields, models
import pandas as pd
import io
import calendar
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat, DEFAULT_SERVER_DATE_FORMAT


class TrialBalanceReport(models.TransientModel):
    _inherit = 'trial.balance.report.wizard.contabilidad.cfdi'
    report_type = fields.Selection(string='Tipo de Reporte', selection=[('balanza', 'Balanza de Comprobación'), ('reporte', 'Estado de Situación Financiera Y Estado de Pérdidas y Ganancias'),('custom', 'Busqueda Personalizada'),('resultados', 'Cuentas de Resultados')])
    
    def generar_reporte_perdidas_y_ganancias_y_estado_financiero(self):
        return self.env.ref('contabilidad_cfdi.situacion_financiera').report_action(self, data={}, config=False)
    
    def dfs_list_edo_perdidas_y_ganancias(self,model,data_for_report_as_data_frame):          
        r1=model.compute_r1(data_for_report_as_data_frame)
        r2_3=model.compute_r2_r3(data_for_report_as_data_frame,r1[1])
        r4=model.compute_r4(data_for_report_as_data_frame)
        r5=model.compute_r5(data_for_report_as_data_frame)
        r6=model.compute_r6(r2_3[1],r4[1],r5[1])
        return [r1[0],r2_3[0],r4[0],r5[0],r6[0],r6[1]]



    def dfs_list_edo_de_situacion_financiera(self,model,resultado_del_ejercio_anterior,data_for_report_as_data_frame):                    
        # list of dataframes
        return [model.compute_total_activo_circulante(data_for_report_as_data_frame),model.compute_total_activo_no_circulante(data_for_report_as_data_frame),model.compute_total_pasivo(data_for_report_as_data_frame),model.compute_total_capital_contable(data_for_report_as_data_frame,resultado_del_ejercio_anterior)]

#1
    def financial_reports_prepare_report_trial_balance(self,model,month):
        model.ensure_one()
        print({
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
        })
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
        df['result_d_c_'] = df['final_balance']-df['initial_balance']
        df['group_code_prefix']=df['account_group_id'].apply(self.get_group_code_prefix)   
        df['group_name']=df['account_group_id'].apply(self.get_account_name)             
        df['debit']=df['debit']   
        df['credit']=df['credit']    
        df['final_balance']=df['final_balance']  
        df['initial_balance']=df['initial_balance']
        df['debit-credit']=df['debit']-df['credit']
        return (df[['group_code_prefix','name','result_d_c_','debit','credit','debit-credit','initial_balance','final_balance']])

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
        R1=['4-100','5-100']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        df_ventas_netas=df_r1[df_r1['group_code_prefix']=='4-100']
        ventas_netas=df_ventas_netas['result_d_c_']._values[0]
        df_costo_de_ventas=df_r1[df_r1['group_code_prefix']=='5-100']
        costo_de_ventas=df_costo_de_ventas['result_d_c_']._values[0]
        new_row = {'name':'RESULTADO BRUTO (R1)', 'group_code_prefix':"VENTAS - COSTO DE VENTAS = R1", 'result_d_c_':ventas_netas-costo_de_ventas}
        df_r1=df_r1.append(new_row,ignore_index=True)
        return (df_r1,ventas_netas-costo_de_ventas)
        
        
    def compute_r2_r3(self,df,R1_result):
        R2=['5-200-001','5-200-002','5-200-003','5-300']
        df_r2 =self.generate_data_frame_for_acoount_group(R2,df)
        total_gastos_de_operacion=self.sum_final_balance(df_r2)    
        new_row = {'name':'TOTAL GASTOS DE OPERACIÓN (R2)', 'group_code_prefix':"Ʃ GASTOS = R2", 'result_d_c_':total_gastos_de_operacion}
        df_r2=df_r2.append(new_row,ignore_index=True)
        new_row = {'name':'RESULTADO DE OPERACIÓN (R3)', 'group_code_prefix':"R1 - R2 = R3", 'result_d_c_':R1_result-total_gastos_de_operacion}
        df_r2=df_r2.append(new_row,ignore_index=True)        
        return (df_r2,R1_result-total_gastos_de_operacion)
        



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
        

    def compute_r5(self,df):
        R5=['4-400','5-500']
        df_r5 = self.generate_data_frame_for_acoount_group(R5,df)
        df_otros_ingresos=df_r5[df_r5['group_code_prefix']=='4-400']
        otros_ingresos=df_otros_ingresos['result_d_c_']._values[0]        
        df_otros_gastos=df_r5[df_r5['group_code_prefix']=='5-500']
        otros_gastos=df_otros_gastos['result_d_c_']._values[0]
        new_row = {'name':'TOTAL PARTIDAS EXTRAORDINARIAS (R5)', 'group_code_prefix':"OI - OG = R5", 'result_d_c_':otros_ingresos-otros_gastos}
        df_r5=df_r5.append(new_row,ignore_index=True)
        return (df_r5,otros_ingresos-otros_gastos)

    def compute_r6(self,R3_result,R4_result,R5_result):
        df = pd.DataFrame()
        new_row = {'name':'RESULTADO ANTES DE IMPUESTOS', 'group_code_prefix':"R3 + R4 + R5 = R6", 'result_d_c_':R3_result+R4_result+R5_result}
        df=df.append(new_row,ignore_index=True)
        return (df,R3_result+R4_result+R5_result)
        
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
        compute_r1_cdv=self.compute_r1_cdv(data_for_report_as_data_frame)
        compute_r2_cdv=self.compute_r2_cdv(data_for_report_as_data_frame)
        compute_r3_cdv=self.compute_r3_cdv(data_for_report_as_data_frame,compute_r1_cdv,compute_r2_cdv)
        compute_r4_cdv=self.compute_r4_cdv(data_for_report_as_data_frame)
        costo_de_ventas_obj.total=compute_r3_cdv-compute_r4_cdv
        costo_de_ventas_vista_line.create({'cdv_vista_id':costo_de_ventas_obj.id,'concepto':'MATERIAL CONSUMIDO','importe':compute_r1_cdv,'tipo':'mat_consu'})
        costo_de_ventas_vista_line.create({'cdv_vista_id':costo_de_ventas_obj.id,'concepto':'COSTO DE PRODUCCION','importe':compute_r3_cdv,'tipo':'costo_dpr'})
        costo_de_ventas_vista_line.create({'cdv_vista_id':costo_de_ventas_obj.id,'concepto':'INVENTARIOS','importe':compute_r4_cdv,'tipo':'inventario'})
        

    def compute_r1_cdv(self,df):
        #Material Consumido
        R1=['1-220-001']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        data_frame=df_r1[df_r1['group_code_prefix']=='1-220-001']
        #result_d_c_  movimientos del mes
        balance_inicial=float(data_frame['initial_balance']._values[0])
        balance_final=float(data_frame['final_balance']._values[0])
        cargos_del_mes=float(data_frame['debit']._values[0])
        print(balance_inicial)
        print(balance_final)
        print(cargos_del_mes)
        print(balance_inicial+cargos_del_mes)
        print(balance_inicial+cargos_del_mes+balance_final)

        return (balance_inicial+(cargos_del_mes+balance_final))

    def compute_r2_cdv(self,df):
        R1=['5-100-006','5-100-002','5-100-003','5-100-004','5-100-005','5-100-007','5-100-008']
        df_r1 = self.generate_data_frame_for_account_account(R1,df)
        result=df_r1['debit-credit'].sum()       
        return result

    def compute_r3_cdv(self,df,compute_r1_cdv,compute_r2_cdv):
        #COSTO DE PRODUCCION
        R1=['1-220-002']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        data_frame=df_r1[df_r1['group_code_prefix']=='1-220-002']
        #result_d_c_  movimientos del mes
        cargos_del_mes=data_frame['debit']._values[0]
        abonos_del_mes=data_frame['credit']._values[0]
        movimientos_del_mes=data_frame['result_d_c_']._values[0]
        result=compute_r1_cdv+compute_r2_cdv+movimientos_del_mes
        return compute_r1_cdv+compute_r2_cdv+movimientos_del_mes

    def compute_r4_cdv(self,df):
        #INVENTARIOS
        R1=['1-220-003']
        df_r1 = self.generate_data_frame_for_acoount_group(R1,df)
        data_frame=df_r1[df_r1['group_code_prefix']=='1-220-003']
        movimientos_del_mes=data_frame['result_d_c_']._values[0]
        movimientos_del_mes
        return movimientos_del_mes

















    @api.multi
    def button_export_html_ctas_resultado(self):
        self.ensure_one()
        action = self.env.ref(
            'contabilidad_cfdi.action_report_trial_balance')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env['report_trial_balance_contabilidad_cfdi']
        x= self._prepare_report_trial_balance()
        print(x)
        report = model.create(x)
        context1['is_cuentas_de_orden'] = self.cuentas_de_orden
        context1['is_contabilidad_electronica'] = True
        print(context1)
        report.with_context(context1).compute_data_for_report()

        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        context1['default_fecha_ano'] = self.year
        context1['default_fecha_mes'] = self.month
        
        print(context1)
        
        vals['context'] = context1
        ids_a_eliminar=[]
        self.env.cr.execute("SELECT id FROM report_trial_balance_account_contabilidad_cfdi where report_id = "+str(report.id)+" and account_group_id in (select id from account_group where code_prefix like '5%' or code_prefix like '4%' or code_prefix like '8%')")
        result=self.env.cr.dictfetchall()
        for item in result:
            ids_a_eliminar.append(item.get('id'))
        self.env.cr.execute("SELECT id FROM report_trial_balance_account_contabilidad_cfdi where report_id = "+str(report.id)+" and account_id in (select id from account_account where code like '5%' or code like '4%' or code like '8%')")
        result=self.env.cr.dictfetchall()
        for item in result:
            ids_a_eliminar.append(item.get('id'))
        print(ids_a_eliminar)
        print(("DELETE FROM public.report_trial_balance_account_contabilidad_cfdi WHERE id in ("+str(ids_a_eliminar)+" )"))
        ids_a_eliminar = str(ids_a_eliminar)
        ids_a_eliminar= ids_a_eliminar.replace('[','(')
        ids_a_eliminar=ids_a_eliminar.replace(']',')')
        print(ids_a_eliminar)
        self.env.cr.execute("DELETE FROM public.report_trial_balance_account_contabilidad_cfdi WHERE id not in "+ids_a_eliminar)
        return vals