# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime, timedelta


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    origen_hoja_de_proyecto = fields.Many2one('escenario_de_ventas.hoja_de_proyecto')
    
    def open_hoja_de_proyecto(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hoja de Proyecto',
            'res_model': 'escenario_de_ventas.hoja_de_proyecto',
            'res_id': self.origen_hoja_de_proyecto.id,#rec_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            #'view_id': form_id.id,
            'context': {},
            # if you want to open the form in edit mode direclty
            'flags': {'initial_mode': 'edit'},
            'target': 'current',
        }