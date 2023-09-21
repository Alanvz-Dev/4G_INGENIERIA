# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    hoja_de_proyecto_count = fields.Integer(compute='compute_count')
    active = fields.Boolean(string='Archivado')

    def get_hoja_de_proyecto(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hoja de Proyecto',
            'view_mode': 'tree,form',
            'res_model': 'escenario_de_ventas.hoja_de_proyecto',
            'domain': [('crm_lead_id', 'in', [self.id])],
            # 'context': {'crm_lead_id': self.id}
        }

    def compute_count(self):
        x = self.env['escenario_de_ventas.hoja_de_proyecto'].search_count(
            [('crm_lead_id', '=', self.id)])

        self.hoja_de_proyecto_count = self.env['escenario_de_ventas.hoja_de_proyecto'].search_count([

                                                                                          ('crm_lead_id', '=', self.id)])
    
    @api.constrains('stage_id')
    def _check_stage_id(self):
        hoja_de_proyecto= self.env['escenario_de_ventas.hoja_de_proyecto'].search([('crm_lead_id', '=', self.id)])
        product = self.env['product.product'].search([('origen_hoja_de_proyecto','in',hoja_de_proyecto.ids)])
        if self.stage_id.name in ["PERDIDAS","Perdidas",'perdidas']:        
            for item in hoja_de_proyecto:
                self.active=False
                item.active=False
                for pedido in item.pedido_de_venta:
                    pedido.active=False
                for proyecto in item.proyecto_asociado:
                    proyecto.active=False
                for presupuesto in item.presupuesto_asociado:
                    presupuesto.active=False
            
            product.active=False
        elif not self.active:
            self.active=True
            for item in hoja_de_proyecto:
                item.active=True
                for pedido in item.pedido_de_venta:
                    pedido.active=True
                for proyecto in item.proyecto_asociado:
                    proyecto.active=True
                for presupuesto in item.presupuesto_asociado:
                    presupuesto.active=True
            product.active=True