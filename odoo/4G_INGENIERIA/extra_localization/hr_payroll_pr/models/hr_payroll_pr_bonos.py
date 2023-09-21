from odoo import  fields, models


class Bonos(models.Model):
    _name = 'hr_payroll_pr.bonos'
    _description = 'Bonos'
    mayordomia_line_id = fields.Many2one('hr_payroll_pr.mayordomia_line', string='Mayordomía')
    name = fields.Char(string='Nombre')
    codigo = fields.Char(string='Código')