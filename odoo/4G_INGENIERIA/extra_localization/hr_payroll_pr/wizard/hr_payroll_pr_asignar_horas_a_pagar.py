from os import unlink
from odoo import _, api, fields, models

class AsignarPagar(models.TransientModel):
    _name = 'hr_payroll_pr.asign_horasp'
    mayordomia_line_ids = fields.Many2many('hr_payroll_pr.mayordomia_line')
    
    horas = fields.Float(
        string='Horas A Pagar'
    )

    def asign(self):
        for record in self.mayordomia_line_ids:
            record.horas_a_pagar = self.horas
    
