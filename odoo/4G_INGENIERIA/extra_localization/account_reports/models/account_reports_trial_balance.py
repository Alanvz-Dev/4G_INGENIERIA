from odoo import _, api, fields, models
import calendar

class TrialBalance(models.Model):
    _name = 'account_reports.trial_b'
    _description = 'New Description'
    _order = 'sequence, code ASC, name'

    acc_report_id = fields.Many2one(
        comodel_name='account_reports.report',
        ondelete='cascade',
        index=True
    )
    # Data fields, used to keep link with real object
    sequence = fields.Integer(index=True, default=1)

    # Data fields, used to keep link with real object
    account_id = fields.Many2one(
        'account.account',
        index=True
    )

    account_group_id = fields.Many2one(
        'account.group',
        index=True
    )
    parent_id = fields.Many2one(
        'account.group',
        index=True
    )
    # Data fields, used for report display
    code = fields.Char()
    name = fields.Char()
    initial_balance = fields.Float(digits=(16, 2))
    debit = fields.Float(digits=(16, 2))
    credit = fields.Float(digits=(16, 2))
    final_balance = fields.Float(digits=(16, 2))

    def generar_balanza_de_comprobacion(self,report_obj):
        dict_prepare_report_trial_balance={
        'date_from': report_obj.ano+'-'+report_obj.mes+'-01',
        'date_to': report_obj.ano+'-'+report_obj.mes+'-'+str(calendar.monthrange(int(report_obj.ano),int(report_obj.mes))[1]),
        'only_posted_moves': False, 
        'hide_account_at_0': True, 
        'foreign_currency': False, 
        'company_id': 1, 
        'filter_account_ids': [(6, 0, [])], 
        'filter_partner_ids': [(6, 0, [])], 
        'filter_journal_ids': [(6, 0, [])], 
        'fy_start_date': report_obj.ano+'-'+'01'+'-01', 
        'hierarchy_on': 'computed', 
        'limit_hierarchy_level': False, 
        'show_hierarchy_level': 1, 
        'show_partner_details': False, 
        'contabilidad_electronica': True
        }
        trial_balance_report=self.env['trial.balance.report.wizard.contabilidad.cfdi']
        model = trial_balance_report.env['report_trial_balance_contabilidad_cfdi']
        report = model.create(dict_prepare_report_trial_balance)
        context= {'active_model': 'report_trial_balance_contabilidad_cfdi', 'is_cuentas_de_orden': True, 'is_contabilidad_electronica': True}
        report.with_context(context).compute_data_for_report()
        trial_balance_report._cr.execute("SELECT"+" "+str(report_obj.id)+" "+"as acc_report_id,* FROM report_trial_balance_account_contabilidad_cfdi where report_id = "+str(report.id))
        computed_data = trial_balance_report.env.cr.dictfetchall()
        for item in computed_data:
            self.create(item)