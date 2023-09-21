from odoo import _, api, fields, models

class account_reports(models.Model):
    _name = 'account_reports.report'
    name = fields.Char()
    _rec_name = 'name'
    mes = fields.Selection([
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ], string='Mes',required=True)

    ano = fields.Selection([
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
    ], string='Año',required=True)

    total = fields.Float( digits=(2, 2))
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Validado'),
        ('cancel', 'Cancelado')
    ], string='Estatus',default='draft')
   
    concepto_lines = fields.One2many('account_reports.concepto','report_id')
    trial_balance_lines  = fields.One2many('account_reports.trial_b', 'acc_report_id')
    concepto_r = fields.One2many('account_reports.operar_concepto','cr_report_id')

    def generar_balanza_de_comprobacion(self):
        self.trial_balance_lines.generar_balanza_de_comprobacion(self)

    @api.model
    def create(self, values):
        # CODE HERE        
        rec = super(account_reports, self).create(values)
        rec.generar_balanza_de_comprobacion()
        return rec

    
