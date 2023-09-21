from odoo import _, api, fields, models


class Nomina(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def reporte(self):
        import base64
        import psycopg2 as pg
        import pandas.io.sql as psql
        import pandas as pd
        import time
        import io

        pd.set_option('display.max_rows', None)
        connection = pg.connect("host=192.168.1.9 port=5532 dbname=4G_INGENIERIA user=odoo password=58877216/Abca1373")  

        def get_worked_days(employe_id,slip_run_id):
            query= """select sum(hpwd.number_of_days) from hr_payslip slip inner join hr_payslip_worked_days hpwd 
        on slip.id = hpwd.payslip_id where slip.employee_id in (%s)
        and slip.payslip_run_id  in (%s) and hpwd.code in ('WORK100','FJC','SEPT')"""%(employe_id,slip_run_id)
            worked_days = psql.read_sql(query, connection)
            for row  in worked_days.itertuples():
                return row[1] or 0



        query = """select employee.no_empleado,employee.id id,employee."name" empleado,sline.code codigo,srule."name" regla_salarial,
        srule.forma_pago forma_pago,sline.total total,srule.id rule_id,employee.no_cuenta cuenta_banco,rpb.acc_number cuenta_vales
        from hr_payslip_line sline
        inner join hr_salary_rule srule on sline.salary_rule_id = srule.id
        inner join hr_employee employee on sline.employee_id = employee.id
        inner join res_partner_bank rpb on rpb.id = employee.bank_account_id 
        where sline.slip_id in (select id from hr_payslip where payslip_run_id in (%s))
        order by sline.code""" %(self.id)
        query2 = """select distinct (code) codigo from hr_payslip_line line where slip_id  in (
        select id from hr_payslip where payslip_run_id=%s
        )
        """%(self.id)
        df_codigos_unicos = psql.read_sql(query2, connection).sort_values(by=['codigo'])
        arr_codigos_unicos = df_codigos_unicos.sort_values(by=['codigo'])['codigo'].tolist()
        df_arr = []
        df_all_nombre_codigo = False
        for code in arr_codigos_unicos:
            query3 = "select code codigo, name nombre from hr_salary_rule where code in ('%s') and active = true limit 1" % (code)
            df_codigos_nombres = psql.read_sql(query3, connection).sort_values(by=['codigo'])
            df_arr.append(df_codigos_nombres)
        df_all_nombre_codigo=[]
        for row  in pd.concat(df_arr).itertuples():
            df_all_nombre_codigo.append(row[2] or "Error")
        df_all_nombre_codigo = pd.concat(df_arr)['nombre'].tolist()
        full_dataframe = psql.read_sql(query, connection)
        all_employee_ids = set(full_dataframe['id'].tolist())
        count = 0
        count_employee=len(all_employee_ids)
        arr_new_rows = []
        for employee_id in all_employee_ids:    
            df_current_employee = full_dataframe[full_dataframe.id==employee_id]
            arr_current_employee_slip_codes = df_current_employee['codigo'].tolist()   
            arr_codigos_no_encontrados = df_codigos_unicos.query('codigo not in @arr_current_employee_slip_codes') 
            for row  in arr_codigos_no_encontrados.iterrows():
                new_row = {'id': df_current_employee.iloc[0]['id'],'empleado': df_current_employee.iloc[0]['empleado'], 'codigo': row[1]['codigo'], 'regla_salarial': "[row[1]['nombre']]",'forma_pago':"[row[1]['forma_pago']]" ,'total':0}
                arr_new_rows.append(new_row)
                #TODO usar concat en lugar de append              
                # df_new_row = pd.DataFrame(arr_new_rows)
                # full_dataframe = pd.concat([full_dataframe, df_new_row])        
            count=count+1
        full_dataframe_added_records = full_dataframe.append(arr_new_rows, ignore_index=True)    
        columns = ['no_empleado']+['empleado']+df_all_nombre_codigo+['efectivo_plan_privado']+['cuenta_vales']+['cuenta_banorte']+['dias_a_pagar']
        df_report = pd.DataFrame(columns=columns)
        new_row = []
        for employee_id in all_employee_ids:
            employee_vals = {}
            df_current_employee = full_dataframe_added_records[full_dataframe_added_records.id==employee_id].sort_values(by=['codigo'])
            indexx = 0
            for row  in df_current_employee.itertuples():
                employee_vals.update({
                    df_all_nombre_codigo[indexx]:row[7] or 0
                })
                indexx=indexx+1    
            employee_vals.update({
                'no_empleado':row[1] or "Error",
                'empleado':row[3] or "Error",
                # 'efectivo_plan_privado':row[2] or "Error"
                'cuenta_vales':row[10] or "Error",
                'cuenta_banorte':row[9] or "Error",
                'dias_a_pagar':get_worked_days(employee_id,self.id)
            })    
            new_row.append(employee_vals)
        df_report = df_report.append(new_row, ignore_index=True)

        
        df =df_report
        
        fp = io.BytesIO()
        df.to_excel(fp)
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
        
