# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class hr_payslip_extends(models.Model):
    _inherit = 'hr.payslip.run'
    axtraxng_attendance = fields.One2many('hr.axtraxng_attendance','hr_payslip_id')


