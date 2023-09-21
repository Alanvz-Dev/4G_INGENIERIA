# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date, time, timedelta
import calendar

class mrp_production(models.Model):
	_name='mrp.production'
	_inherit='mrp.production'
	entrega=fields.Char(string='Nombre persona entrego:')
	recibe=fields.Char(string='Nombre persona recibio:')
				

		






