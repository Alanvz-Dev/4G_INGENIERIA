# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime, timedelta

import math

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    active = fields.Boolean(default=True)
    hoja_de_proyecto_origen = fields.Many2one(
        'escenario_de_ventas.hoja_de_proyecto')
    state_hp = fields.Selection([('Cotizado', 'Cotizado'),            ('Con Alta Probabilidad', 'Con Alta Probabilidad'),            (
        'Con Orden de Compra', 'Con Orden de Compra'),            ('Con Orden De Compra Listo Para Producion', 'Con Orden De Compra Listo Para Produción')],string="Estado de Proyecto")
    fecha_de_arranque = fields.Date(string='Fecha de Inicio del Proyecto')
    escenario_de_ventas_ids = fields.One2many('escenario_de_ventas.escenario_de_ventas', 'sale_id')    
    cantidad_por_facturar = fields.Float(compute='_compute_cantidad_por_facturar', string='')
    
    def _compute_cantidad_por_facturar(self):
        try:
            product = self.env['product.product'].search(
                    [('origen_hoja_de_proyecto', 'in', [self.hoja_de_proyecto_origen.id])])
            if not product:
                raise UserError(('Por favor Asocie la hoja de proyecto al Producto.'))

            sale_order_line = self.order_line.search([('order_id', 'in', [self.id]), ('product_id', 'in', [product.id])])
            print(sale_order_line)
            sale_order_line.ensure_one()
            self.cantidad_por_facturar=sale_order_line.product_uom_qty-sale_order_line.qty_invoiced
            print(self.cantidad_por_facturar)
            print(self.cantidad_por_facturar)
        except:
            pass
    


    def crear_programacion(self):
        if not self.escenario_de_ventas_ids:
            piezas_por_dia_linea = self.hoja_de_proyecto_origen.piezas_por_dia_linea
            if piezas_por_dia_linea<=0.0:
                raise UserError(('Piezas Por Día Linea No puede ser 0'))
                
            total_de_racks = self.hoja_de_proyecto_origen.total_piezas
            
            sub_tota_dias=math.ceil(total_de_racks/piezas_por_dia_linea)

            inicio = datetime.strptime(self.fecha_de_arranque, '%Y-%m-%d').date()
            fin    = inicio+ timedelta(days=sub_tota_dias)

            lista_fechas = [inicio + timedelta(days=d) for d in range((fin - inicio).days )]
            lista_de_fechas_habiles=[]
            lista_de_fechas_no_habiles=[]
            contador=0
            while True:
                if inicio.isoweekday() in [1,2,3,4,5]:
                    lista_de_fechas_habiles.append(inicio)
                    contador=contador+1
                    inicio = inicio + timedelta(days=1)
                elif inicio.isoweekday() in [6,7]:
                    lista_de_fechas_no_habiles.append(inicio)
                    contador=contador+1
                    inicio = inicio + timedelta(days=1)

                if len(lista_de_fechas_habiles)==len(lista_fechas):
                    break
            contador=0
            for dia in lista_de_fechas_habiles:
                piezas_por_dia_linea = self.hoja_de_proyecto_origen.piezas_por_dia_linea
                contador=contador+self.hoja_de_proyecto_origen.piezas_por_dia_linea
                if contador>total_de_racks:
                    piezas_por_dia_linea=total_de_racks%self.hoja_de_proyecto_origen.piezas_por_dia_linea


                escenario_de_ventas_line={            
                'product_id': self.product_id.id,
                'start_date': dia,
                'piezas_por_dia_linea': piezas_por_dia_linea,
                'costo_total': piezas_por_dia_linea * self.hoja_de_proyecto_origen.precio_por_pieza_mxn,
                'cliente':self.hoja_de_proyecto_origen.nombre_de_cliente.id,
                'state_hp':self.state_hp
                }
                new_escenario_de_ventas_ids = self.escenario_de_ventas_ids.create(escenario_de_ventas_line)
                self.escenario_de_ventas_ids = [(4, new_escenario_de_ventas_ids.id)]
        
        else:
            raise UserError(('No se puede crear una programacíon si ya existen registros, si lo desea elimine todos los registros e intente de nuevo'))
            

    def eliminar_programacion(self):
        if self.escenario_de_ventas_ids:
            self.escenario_de_ventas_ids.unlink()

    def test(self):
        x = self.env['escenario_de_ventas.flujo_de_efectivo']
        x.test()

    
        
            
            
            
            
                       
        
 
        
        
                        
