from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

class Turno(models.Model):
    _name = 'hr_payroll_pr.turno'
    _description = 'Turnos'
    name = fields.Char(string='Turno')
    turno_line_ids = fields.One2many('hr_payroll_pr.turno_line', 'turno_id',ondelete='cascade',copy=True)    
    horas_por_dia = fields.Float(string='Horas Por Día')
    suma_horas = fields.Float(string='Suma Horas Por Día')
    
    
    @api.one
    def is_dia_laborable(self,date):
        if self.dia_de_la_semana(date) in self.turno_line_ids.mapped('dia'):
            return True
        return False
    @api.one
    def dia_de_la_semana(self,date):
        try:
             return str(datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT).weekday())
        except:
            pass
    @api.one
    def dia_de_la_semana_nombre(self,date):
        dia = self.dia_de_la_semana(date)
        if dia in ['0']:
            return 'Lunes'
        if dia in ['1']:
            return 'Martes'
        if dia in ['2']:
            return 'Miércoles'
        if dia in ['3']:
            return 'Jueves'
        if dia in ['4']:
            return 'Viernes'
        if dia in ['5']:
            'Sábado'
        if dia in ['6']:
            return 'Domingo'