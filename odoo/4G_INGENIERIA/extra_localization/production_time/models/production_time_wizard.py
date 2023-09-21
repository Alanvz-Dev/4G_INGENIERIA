# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class ProductionTimeWizard(models.TransientModel):
    _name = 'production_time.wizard'
    # state_hp = fields.Selection([('Cotizado', 'Cotizado'), ('Con Alta Probabilidad', 'Con Alta Probabilidad'),            (
    producto = fields.Many2many('product.product')
    centro_de_trabajo = fields.Many2many('mrp.workcenter')
    state_hp_ids = fields.Many2many('production_time.selection')
    def production_time(self):
        # InsertarRegistrosDB
        domain = []
        if self.state_hp_ids:
            domain.append(('state_hp', 'in', self.state_hp_ids.mapped('name')))
        hp_with_so = self.env['escenario_de_ventas.hoja_de_proyecto'].search(
            [('pedido_de_venta', 'not in', [False])]).mapped('pedido_de_venta')
        self.env['production_time.data'].search([]).unlink()
        for sale in hp_with_so.search(domain):
            if sale.escenario_de_ventas_ids and sale.hoja_de_proyecto_origen.mano_de_obra_ids:
                print(self.centro_de_trabajo)                
                for mano_de_obraline in sale.hoja_de_proyecto_origen.mano_de_obra_ids:
                    for mrp_id in self.centro_de_trabajo.ids:
                        if mrp_id in mano_de_obraline.mano_de_obra.ids:                        
                            horas_x_pieza = mano_de_obraline.horas_hombre_total / \
                                mano_de_obraline.hoja_de_proyecto.total_piezas
                            # mano_de_obraline.mano_de_obra
                            for line in sale.escenario_de_ventas_ids:
                                dias_antelacion = self.env['production_time.wcent_config'].search(
                                    [('centro_de_produccion', 'in', [mano_de_obraline.mano_de_obra.id])])
                                fecha = line.start_date
                                if dias_antelacion:
                                    fecha = (datetime.strptime(line.start_date, '%Y-%m-%d')-relativedelta(
                                        days=dias_antelacion.antelacion)).strftime('%Y-%m-%d')
                                print('Fecha Prog\t', fecha, '\t', 'Producto\t', line.product_id.name+" ", 'Centro de Prod.\t', mano_de_obraline.mano_de_obra.name+" ", 'Piezas Por Dia\t',
                                      str(line.piezas_por_dia_linea)+" ", 'Horas X Dia\t', str(line.piezas_por_dia_linea*horas_x_pieza)+" ", '\tEstado HP\t', sale.state_hp)
                                vals = {
                                    'fecha_programada': fecha,
                                    'producto': line.product_id.id,
                                    'centro_de_produccion': mano_de_obraline.mano_de_obra.id,
                                    'piezas_por_dia': line.piezas_por_dia_linea,
                                    'horas_capacidad_instalada':mano_de_obraline.mano_de_obra.capacity - mano_de_obraline.mano_de_obra.time_start - mano_de_obraline.mano_de_obra.time_stop,
                                    'horas_por_dia': (line.piezas_por_dia_linea*horas_x_pieza),
                                    'state_hp': sale.state_hp
                                }
                                print(vals)
                                created=self.env['production_time.data'].create(vals)
                                print(created)


class ProductionTimeWizard(models.Model):
    _name = 'production_time.data'
    fecha_programada = fields.Date(string='Fecha Programada')
    producto = fields.Many2one('product.product')
    centro_de_produccion = fields.Many2one('mrp.workcenter')
    piezas_por_dia = fields.Float(string='Piezas Por Día')
    horas_capacidad_instalada = fields.Float(string='Capacidad Instalada [HR]')
    horas_por_dia = fields.Float(string='Capacidad Requerida [HR]')
    state_hp = fields.Many2many('production_time.selection')

    def get_data_custom_widget(self):
       ret_list = []
       req = ("select producto,centro_de_produccion,horas_capacidad_instalada,horas_por_dia from production_time_data")
       self.env.cr.execute(req)
       for rec in self.env.cr.dictfetchall():
           ret_list.append(rec)
       return ret_list
        # return self.env['production_time.data'].search([])

    
class ProductionTimeWizardSel(models.Model):
    _name = 'production_time.selection'
    name= fields.Char(string='Estado de Proyecto')

