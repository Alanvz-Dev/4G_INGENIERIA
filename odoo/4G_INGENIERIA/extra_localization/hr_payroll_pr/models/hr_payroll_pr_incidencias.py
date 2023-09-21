from odoo import fields, models

class ModuleName(models.Model):
    _name = 'hr_payroll_pr.incidencias'
    _description = 'New Description'
    name = fields.Char(string='Nombre')
    codigo = fields.Char(string='Código')