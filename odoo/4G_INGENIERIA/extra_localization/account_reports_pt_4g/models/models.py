# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import pandas as pd
import io
import calendar

class TrialBalanceReport(models.TransientModel):
    _inherit = 'trial.balance.report.wizard.contabilidad.cfdi'
    
    def sum_movimientos_del_mes(self,df):
        return df['movimientos_del_mes'].sum()
    
    def get_account_name_pt(self,account_id):
        return self.env['account.group'].browse(int(account_id)).name or 'N/A'
    
    def get_group_code_prefix_pt(self,account_id):
        return self.env['account.group'].browse(int(account_id)).code_prefix

    def get_account_account_code_prefix_pt(self,account_id):
        return self.env['account.account'].browse(int(account_id)).code

    def get_account_account_code_prefix_pt(self,account_id):
        return self.env['account.account'].browse(int(account_id)).code

    def get_account_account_name_pt(self,account_id):
        return self.env['account.account'].browse(int(account_id)).name or 'N/A'
    
    def generar_reporte_pt(self):
        return self.env.ref('contabilidad_cfdi.id_pt_view_report').report_action(self, data={}, config=False)

    def generate_data_for_report_as_data_frame_pt(self,trial_balance_report,dict_prepare_report_trial_balance):        
        report = trial_balance_report.env['report_trial_balance_contabilidad_cfdi'].create(dict_prepare_report_trial_balance)
        report.with_context({'active_model': 'report_trial_balance_contabilidad_cfdi', 'is_cuentas_de_orden': True, 'is_contabilidad_electronica': True}).compute_data_for_report()
        trial_balance_report._cr.execute("SELECT * FROM report_trial_balance_account_contabilidad_cfdi where report_id = "+str(report.id))
        computed_data = trial_balance_report.env.cr.dictfetchall()                        
        return pd.DataFrame(computed_data)

    def financial_reports_prepare_report_trial_balance_pt(self,model,month):
        model.ensure_one()
        ARRAY_ACCOUNT_CODE_PREFIX=['4-300-002','4-400-001']
        accounts_ids = self.env['account.account'].search([('code','in',ARRAY_ACCOUNT_CODE_PREFIX)]).ids
        # model.accounts_ids=[(4,[x for x in accounts_ids])]
        # self.env.cr.commit()
        return {
            'date_from': model.year+'-'+month+'-01',
            'date_to': model.year+'-'+month+'-'+str(calendar.monthrange(int(model.year),int(month))[1]),
            'only_posted_moves': model.target_move == 'posted',
            'hide_account_at_0': model.hide_account_at_0,
            'foreign_currency': model.foreign_currency,
            'company_id': model.company_id.id,
            'filter_account_ids': [(6, 0,accounts_ids)],
            'filter_partner_ids': [(6, 0, model.partner_ids.ids)],
            'filter_journal_ids': [(6, 0, model.journal_ids.ids)],
            'fy_start_date': model.fy_start_date,
            'hierarchy_on': model.hierarchy_on,
            'limit_hierarchy_level': model.limit_hierarchy_level,
            'show_hierarchy_level': model.show_hierarchy_level,
            'show_partner_details': model.show_partner_details,
            'contabilidad_electronica':True
        }

    def generate_data_frame_for_acoount_group_pt(self,ARRAY_GROUP_CODE_PREFIX,df):
        account_group = self.env['account.group'].search([('code_prefix','in',ARRAY_GROUP_CODE_PREFIX)]).ids
        df_filtered_by_ag=df[df.account_group_id.isin(account_group)]
        df_filtered_by_ag['account_code']=df_filtered_by_ag['account_group_id'].apply(self.get_group_code_prefix_pt)   
        df_filtered_by_ag['group_name']=df_filtered_by_ag['account_group_id'].apply(self.get_account_account_name_pt)        
        df_filtered_by_ag['movimientos_del_mes'] = df_filtered_by_ag['final_balance'] - df_filtered_by_ag['initial_balance']                
        return (df_filtered_by_ag[['name','movimientos_del_mes','account_code']])

    def generate_data_frame_for_account_account_pt(self,accounts_ids,df):
        df_filtered_by_acc=df[df.account_id.isin(accounts_ids)]
        df_filtered_by_acc['account_code']=df_filtered_by_acc['account_id'].apply(self.get_account_account_code_prefix_pt)
        df_filtered_by_acc['group_name']=df_filtered_by_acc['account_id'].apply(self.get_account_account_name_pt)
        df_filtered_by_acc['movimientos_del_mes'] = df_filtered_by_acc['final_balance'] - df_filtered_by_acc['initial_balance']        
        return (df_filtered_by_acc[['name','movimientos_del_mes','account_code']])
