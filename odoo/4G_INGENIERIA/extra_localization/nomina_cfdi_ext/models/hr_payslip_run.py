from odoo import _, api, fields, models


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    version_cfdi = fields.Selection(string='Tipo de Version CFDI', selection=[('3', '3.3'), ('4', '4.0')],
    required=True
    )

    slips_count = fields.Integer(compute='_compute_slips_count', string='Cantidad de Nóminas')
    
    def _compute_slips_count(self):
        self.slips_count = len(self.slip_ids)

    def view_slip_ids(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Recibos de Nómina",
            "view_mode": "tree,form",
            "res_model": "hr.payslip",
            "domain": [("id", "in", self.slip_ids.ids)],
            "context": {'create': False}
        }




    @api.multi
    def recalcular_nomina_payslip_batch(self):
        self.slip_ids.hola()
        self.slip_ids.compute_sheet()
        return {

            'name': 'Aviso',

            'type': 'ir.actions.act_window',

            'res_model': 'nomina_cfdi.message',

            'view_mode': 'form',

            'view_type': 'form',

            'target': 'new'

        }
        

    @api.multi
    def timbrar_nomina(self):
        self.ensure_one()
        for payslip_id in self.web_progress_iter(self.slip_ids, msg="TIMBRANDO NÓMINA"):
            try:
                with self.env.cr.savepoint():
                    if payslip_id.state in ['draft', 'verify']:
                        payslip_id.action_payslip_done()
                    if not payslip_id.nomina_cfdi:
                        if self.version_cfdi=='4':
                            
                            payslip_id.action_cfdi_nomina_generate()                
                        if self.version_cfdi=='3':
                            
                            payslip_id.action_cfdi_nomina_generate_cfdi_3_0()                
            except Exception as e:                
                continue
        return {

            'name': 'Aviso',

            'type': 'ir.actions.act_window',

            'res_model': 'nomina_cfdi.message',

            'view_mode': 'form',

            'view_type': 'form',

            'target': 'new'

        }


    @api.multi
    @api.depends('slip_ids.state','slip_ids.estado_factura')
    def _compute_show_cancelar_button(self):
        for payslip_batch in self:
            show_button = True
            for payslip in payslip_batch.slip_ids:
                if payslip.state != 'done'  or payslip.estado_factura!='factura_correcta':
                    show_button=False
                    break
            payslip_batch.show_cancelar_button = show_button