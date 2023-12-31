# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import UserError
#from datetime import datetime

class HorasNomina(models.Model):
    _name = 'horas.nomina'
    _description = 'HorasNomina'
    active = fields.Boolean(default=True)
    name = fields.Char("Name", required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Empleado')
    fecha = fields.Date('Fecha')
    tipo_de_hora = fields.Selection([('1','Simple'),
                                      ('2','Doble'),
                                      ('3', 'Triple')], string='Tipo de hora extra')
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho'), ('cancel', 'Cancelado')], string='Estado', default='draft')
    horas = fields.Char("Horas")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('horas.nomina') or _('New')
        result = super(HorasNomina, self).create(vals)
        return result

    @api.multi
    def action_validar(self):
        self.write({'state':'done'})
        return

    @api.multi
    def action_cancelar(self):
        self.write({'state':'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state':'draft'})

    @api.multi
    def unlink(self):
        raise UserError("Los registros no se pueden borrar, solo cancelar.")
    

# import datetime
# eventos=self.env['calendar.event'].search([])

# for evento in eventos:
#     try:
#         print('Anterior'+evento.display_start)
#         evento.update({'display_start':(datetime.datetime.strptime(evento.display_start, '%Y-%m-%d %H:%M:%S')-datetime.timedelta(hours=1))})
#         evento.update({'start':(datetime.datetime.strptime(evento.start, '%Y-%m-%d %H:%M:%S')-datetime.timedelta(hours=1))})
#         evento.update({'stop':(datetime.datetime.strptime(evento.stop, '%Y-%m-%d %H:%M:%S')-datetime.timedelta(hours=1))})
#         evento.update({'start_datetime':(datetime.datetime.strptime(evento.start_datetime, '%Y-%m-%d %H:%M:%S')-datetime.timedelta(hours=1))})
#         evento.update({'stop_datetime':(datetime.datetime.strptime(evento.stop_datetime, '%Y-%m-%d %H:%M:%S')-datetime.timedelta(hours=1))})
#         evento.update({'oe_update_date':(datetime.datetime.strptime(evento.oe_update_date, '%Y-%m-%d %H:%M:%S')-datetime.timedelta(hours=1))})
#         print('Nuevo'+evento.display_start)
#         print(evento.id)

#     except:
#         print(evento.id)

