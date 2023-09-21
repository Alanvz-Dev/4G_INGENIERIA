# -*- coding: utf-8 -*-

from odoo import models, fields, api

class production_time(models.Model):
    _name = 'production_time.production_time'

    producto = fields.Many2many('product.product')
    fecha_programada = fields.Date()
    piezas_x_dia = fields.Float()
    horas_x_dia = fields.Float()
    


#Centro de ProducciónProducto Fecha de fabricación horas hombre Totales Cantidad de Piezas


# domain = []
# domain.append(('pedido_de_venta','not in',[False]))
# # if self.# domain = []state_hp:
# #     domain.append(('state_hp','in',[self.state_hp]))


# hp_with_so=self.env['escenario_de_ventas.hoja_de_proyecto'].search([domain]).mapped('pedido_de_venta')
# domain_sale=[('state_hp','in',['Cotizado'])]


# # hp_with_so=self.env['escenario_de_ventas.hoja_de_proyecto'].search([('pedido_de_venta','not in',[False])]).mapped('pedido_de_venta').mapped('escenario_de_ventas_ids')
# for sale in hp_with_so.search(domain_sale):
#     if sale.escenario_de_ventas_ids and sale.hoja_de_proyecto_origen.mano_de_obra_ids:
#         for mano_de_obraline in sale.hoja_de_proyecto_origen.mano_de_obra_ids:
#             print(mano_de_obraline)
