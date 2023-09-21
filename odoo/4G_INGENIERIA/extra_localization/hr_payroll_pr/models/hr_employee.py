from odoo import fields, models

class Empleado(models.Model):
    _inherit = 'hr.employee'
    is_administrativo = fields.Boolean(string='Es Administrativo',default=False)
    turno = fields.Many2one('hr_payroll_pr.turno')
    
