from odoo import _, api, fields, models

class AsignarProyecto(models.TransientModel):
    _name = 'hr_payroll_pr.asign_proyecto'
    _inherit = 'hr_payroll_pr.horas_proyecto'
    _description = 'Asignar Proyecto'    
    mayordomia_line_ids = fields.Many2many('hr_payroll_pr.mayordomia_line')

    
    @api.one
    def asign(self):
        for record in self.mayordomia_line_ids:
            record.horas_proyecto_ids=[(0,0,{'analytic_account_id':self.analytic_account_id.id,'horas':self.horas,
            'centro_de_trabajo':self.centro_de_trabajo.id})]    
    
