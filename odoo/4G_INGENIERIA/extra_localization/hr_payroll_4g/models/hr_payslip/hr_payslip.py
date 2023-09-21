# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import pytz

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    faltas_injustificadas=fields.Float()
    faltas_justificadas=fields.Float()
    faltas_con_goce_de_sueldo=fields.Float()
    vacaciones=fields.Float()