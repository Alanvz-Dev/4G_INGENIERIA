from odoo import _, api, fields, models
import numbers


class ModuleName(models.Model):
    _name = 'account_reports.operar_concepto_aritmetica'
    operar_concepto_id = fields.Many2one('account_reports.operar_concepto',domain="[('id', '>', 0)]")     
    aritmetica_de_la_operacion = fields.Selection([
        ('suma', '+'),
        ('resta', '-')],required=True)
    total = fields.Float(digits=(2, 2))


    @api.onchange('operar_concepto_id')
    def _compute_total(self):
        print(self)
    



    # @api.onchange('operar_concepto_id')
    # def _onchange_operar_concepto_id(self):
    #     print(self.operar_concepto_id.cr_report_id.concepto_r)
    #     x = self.operar_concepto_id.cr_report_id.concepto_r.filtered(lambda r: not isinstance(r.id, numbers.Number))
    #     for item in x:
    #         y = item._convert_to_write(item._cache)
    #         print(y)
    #    account_reports.operar_conceptoaccount_reports.operar_conceptoaccount_reports.operar_concepto self.total = x.resultado_aux
    #     print(x)
    #     if isinstance(self.id, numbers.Number):
    #         print("Numerico")
    #     else:
    #         print("NO Numerico")
    #     print(self.id)
    #     print(type(self.id))

    