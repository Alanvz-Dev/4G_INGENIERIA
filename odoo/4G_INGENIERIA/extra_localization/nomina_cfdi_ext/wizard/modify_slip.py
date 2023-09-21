from odoo import _, api, fields, models



class ModifySlip(models.TransientModel):
    _name = 'nomina_cfdi.modify_slip'
    _description = 'Wizard para modificar uso de cfdi'
    slips_ids = fields.Many2many(comodel_name='hr.payslip', string='Nóminas Seleccionadas')
    uso_cfdi = fields.Selection(
        selection=[('P01', _('Por definir')),('CN01', _('Nomina')),],
        string=_('Uso CFDI (cliente)'),required=True
    )
    
    def modify(self):
        for slip in self.slips_ids:
            slip.uso_cfdi = self.uso_cfdi
