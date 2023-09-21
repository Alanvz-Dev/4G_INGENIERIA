from odoo import _, api, fields, models


class DinningServiceSateTime(models.Model):
    _name = 'dinning_service.date_time'
    _description = 'Horas de Servicio'
    _rec_name = 'date_time'
    date_time = fields.Datetime(string='Hora y Fecha de Servicio')
    date_time_service = fields.Many2one('dining_service.line')
