# -*- coding: utf-8 -*-

from odoo import models, fields, api


class pedidos(models.Model):
    _name = 'nuevos_proyectos.pedidos'

    name = fields.Char(compute='_compute_name')

    def _compute_name(self):
        for record in self:
            record.name = record.product_id.categ_id.complete_name

    @api.multi
    def action_MO(self):
        for v in self:
            values = {'state': 'confirmed',
                      'is_locked': True,
                      'product_qty': 1,
                      'date_planned_start': v.n_p_start_date,
                      'date_planned_finished': v.n_p_start_date,
                      'company_id': 1,
                      'location_src_id': 22,
                      'location_dest_id': 12,
                      'picking_type_id': 6,
                      'product_id': v.product_id,
                      'product_uom_id': v.product_id.uom_id.id,
                      'bom_id': 3319,
                      'mae':v.maestros}
            self.env['mrp.production'].create(values)

    product_id = fields.Many2one(
        comodel_name='product.product', string='product')
    pieces = fields.Float('Piezas', Required=True)
    maestros = fields.Integer(string='Personas', required=True)
    n_p_start_date = fields.Date(string='Fecha de construccion', required=True)
    tipo = fields.Selection(string = 'Lugar de fabricación', selection = [('P','Prototipo'), ('L','Linea'), ('E','Escantillon'), ('M','Montaje'), ('A','Arranque'), ('C','Corte'), ('H','Habilitado')], default='L')

  
