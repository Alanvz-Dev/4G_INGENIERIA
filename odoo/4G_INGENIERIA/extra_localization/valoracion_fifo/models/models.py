# -*- coding: utf-8 -*-

from odoo import models, fields, api

class valoracion_fifo(models.Model):
    _name = 'valoracion_fifo.valoracion_fifo'

    product_id = fields.Many2one(comodel_name='product.product', string='Producto')
    cantidad = fields.Float(string='Cantidad')
    ubicacion = fields.Many2one(comodel_name='stock.location', string='Ubicación')
    precio_unitario = fields.Float(string='Precio Unitario')
    valor = fields.Float(string='Valor')
    


    
    def fill_data(self):
        # CODE HERE
        #377898
        record_set = self.search([])
        record_set.unlink()
        internal_locations=self.env['stock.location'].search([('usage','in',['internal'])]).ids
        stock_quant = self.env['stock.quant'].search([('quantity','>',0),('location_id','in',internal_locations)])
        for line in stock_quant:
            vals={
                'product_id': line.product_id.id,
                'cantidad': line.quantity,
                'ubicacion': line.location_id.id,
                'precio_unitario': line.product_id.product_tmpl_id.standard_price,
                'valor': line.product_id.product_tmpl_id.standard_price*line.quantity
            }
            self.create(vals)

    def return_views(self):
        self.fill_data()
        views = [
            #Si no se agrega el form, esta en modo de solo lectura
                 (self.env.ref('valoracion_fifo.list').id, 'list'),
                 (self.env.ref('valoracion_fifo.valoracion_fifo_view_form').id, 'form')]
        return{
                'name': 'Valoracion de Inventario',
                'view_type': 'form',
                "view_mode": "tree,form",
                'view_id': False,
                "res_model": "valoracion_fifo.valoracion_fifo",
                'views': views,
                #'domain': [('id', 'in', invoices.ids)],
                'type': 'ir.actions.act_window',
            }

