from odoo import _, api, fields, models

class OperarConcepto(models.Model):
    _name = 'account_reports.operar_concepto'
    _order = "id asc"
    _rec_name ='concepto'
    concepto = fields.Char()
    resultado_aux = fields.Float(compute='_compute_resultado_aux')
    concepto_r_lines  = fields.One2many('account_reports.concepto_r', 'operar_concepto_id')
    cr_report_id = fields.Many2one('account_reports.report')
    concept_lines  = fields.One2many('account_reports.operar_concepto_aritmetica', 'operar_concepto_id')

    

    @api.one
    def _compute_resultado_aux(self):
        print(self.resultado_concepto()[0])
        print(self.resultado_concepto_r()[0])
        self.resultado_aux=self.resultado_concepto()[0]+self.resultado_concepto_r()[0]
        print(self.resultado_aux)
    
    @api.onchange('concepto_r_lines')
    def onchange_concepto_r_lines(self):
        self._compute_resultado_aux()
        print(self.resultado_aux)
    

    
    @api.one
    def resultado_concepto(self):
        total_group=0
        for item in self.concept_lines:
            if item.aritmetica_de_la_operacion=='suma':
                total_group=total_group+item.total
            if item.aritmetica_de_la_operacion=='resta':
                total_group=total_group-item.total
        return total_group

    @api.one
    def resultado_concepto_r(self):
        total_account=0

        for item in self.concepto_r_lines:
            if item.aritmetica_de_la_operacion=='suma':
                total_account=total_account+item.total
            if item.aritmetica_de_la_operacion=='resta':
                total_account=total_account-item.total
        return total_account



    @api.model
    def create(self, values):
        # CODE HERE
        print(values)
        return super(OperarConcepto, self).create(values)


class ConceptoR(models.Model):
    _name = 'account_reports.concepto_r'
    operar_concepto_id = fields.Many2one('account_reports.operar_concepto')
    concepto_id = fields.Many2one('account_reports.concepto')
    aritmetica_de_la_operacion = fields.Selection([
        ('suma', '+'),
        ('resta', '-')], required=True)
    total = fields.Float(digits=(2, 2))

    @api.onchange('concepto_id')
    def _onchange_concepto_id(self):
        self.total=self.concepto_id.resultado_aux
        print(self.concepto_id.resultado_aux)
    
