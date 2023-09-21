# -*- coding: utf-8 -*-

from odoo import models, fields, api



class dining_service_detail(models.Model):
    _name = 'dining_service.detail'
    _rec_name = 'name'
    name = fields.Char()
    week = fields.Integer()
    dining_service_line = fields.One2many('dining_service.line', 'dining_service_detail', ondelete='cascade',copy=True)
    
    total_4g = fields.Integer(compute='_compute_total_4g', string='4G INGENIERIA')
    def _compute_total_4g(self):
        self.total_4g=len(self.dining_service_line.search([('dining_service_detail','in',self.ids),('company','in',['4G_INGENIERIA'])]).mapped('date_time_service_line'))        
    
    total_ferrextool = fields.Char(compute='_compute_total_ferrextool', string='FERREXTOOL')
    def _compute_total_ferrextool(self):
        self.total_ferrextool=len(self.dining_service_line.search([('dining_service_detail','in',self.ids),('company','in',['FERREXTOOL'])]).mapped('date_time_service_line'))
    
    total_invitados = fields.Char(compute='_compute_total_invitados', string='INV/PRACT')
    def _compute_total_invitados(self):
        self.total_invitados=len(self.dining_service_line.search([('dining_service_detail','in',self.ids),('company','in',['INV/PRACT'])]).mapped('date_time_service_line'))
        pass
    
    total = fields.Char(compute='_compute_total', string='Total de Servicios')
    def _compute_total(self):
        self.total=len(self.dining_service_line.search([('dining_service_detail','in',self.ids),]).mapped('date_time_service_line'))
        pass
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'En Proceso'),
        ('done', 'Cerrado')
    ], 'Estado', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

    @api.multi
    def revert(self):

        self.write({'state': 'draft'})

    @api.multi
    def discount(self):
        self.dining_service_line.clear_services()
        for service in self.dining_service_line:
            service.discount_service()
        self.write({'state': 'done'})



    































































