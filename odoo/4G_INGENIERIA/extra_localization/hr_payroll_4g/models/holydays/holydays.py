# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import pytz

class holydays(models.Model):
    _inherit = 'hr.holidays'
    date_leave_range=fields.Char()
    active = fields.Boolean(default=True)





    def get_exists_holiday(self, fecha, employee_id):
        holydays =self.search([('employee_id','in',[employee_id]),('date_leave_range','ilike',fecha)])
        return holydays

    def get_exists_holiday_list(self, fecha_inicial,fecha_final, employee_id):
        query = "select fecha::date from generate_series('"+str(fecha_inicial)[0:10] + \
                "','"+str(fecha_final)[0:10]+"', '1 day'::interval) fecha"
        self.env.cr.execute(query)
        intervalo_de_fechas = self.env.cr.dictfetchall() or False
        holidays_objs=[self.env['hr.holidays'].search([('employee_id','in',[employee_id]),('state','in',['validate']),('date_leave_range','ilike',fecha.get('fecha')[0:10])]) for fecha in intervalo_de_fechas]
        print(holidays_objs)
        #Return unique values
        return list(set(holidays_objs)) or False


    def utc_to_local(self,date):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(date,
        DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),DEFAULT_SERVER_DATETIME_FORMAT)
        print(display_date_result)

    def local_to_utc(self,date):
        #Las 7:00 am de Ciudad de Mexico son las 13:00:00 en UTC
        local = pytz.timezone("America/Mexico_City")
        naive = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt

