from odoo import models, fields, api
import datetime

class empleados_administrativos(models.Model):
    _name = 'hr_payroll_4g.empleados_administrativos'
    empleado=fields.Many2one('hr.employee')