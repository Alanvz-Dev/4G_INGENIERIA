from odoo import models, fields

class Turnos(models.Model):
    _name = 'hr_payroll_pr.turno_line'
    _description = 'Turnos Line'
    dia = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miércoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo')
        ], 'Day of Week', required=True, index=True, default='0')
    hour_from = fields.Float(string='Work from', required=True, index=True,
        help="Start and End time of working.\n"
             "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    hour_to = fields.Float(string='Work to', required=True)    
    turno_id = fields.Many2one('hr_payroll_pr.turno')
    between_days = fields.Boolean(string='Entre días',help="Se usa cuando el horario laboral se encuentra entre dos días, por ejemplo de 17:00 a 2:00 am, en ese caso debería establecerse.")
    

