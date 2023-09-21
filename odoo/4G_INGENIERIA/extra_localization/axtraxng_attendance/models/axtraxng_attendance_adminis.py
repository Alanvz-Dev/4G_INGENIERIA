from odoo import models, fields, api, _

class axtraxng_attendance_administrative(models.Model):
    _name = 'hr.axtraxng_administrative'
    employee_id_administrative = fields.Many2one('hr.employee')