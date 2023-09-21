# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Account_Moves_Lock(models.Model):
    _name = 'account_moves_lock.account_moves_lock'
    _order = 'id desc'
    month = fields.Selection([ ('enero', 'ENERO'),
    ('febrero', 'FEBRERO'),
    ('marzo', 'MARZO'),
    ('abril', 'ABRIL'),
    ('mayo', 'MAYO'),
    ('junio', 'JUNIO'),
    ('julio', 'JULIO'),
    ('agosto', 'AGOSTO'),
    ('septiembre', 'SEPTIEMBRE'),
    ('octubre', 'OCTUBRE'),
    ('noviembre', 'NOVIEMBRE'),
    ('diciembre', 'DICIEMBRE'),
    ],'Month')
    year = fields.Selection([ ('2020', '2020'),
    ('2021', '2021'),
    ('2022', '2022'),
    ('2023', '2023'),
    ('2024', '2024')
    ],'Year')
    start_date = fields.Date('Inicio de Periodo', required=True)
    end_date = fields.Date('Fin del Periodo', required=True)



