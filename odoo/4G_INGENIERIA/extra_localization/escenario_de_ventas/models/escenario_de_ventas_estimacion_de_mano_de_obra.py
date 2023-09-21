# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api

class Estimacion_De_Mano_De_Obra(models.Model):
    _name = 'escenario_de_ventas.estimacion_de_mano_de_obra'
    mano_de_obra  = fields.Many2one('mrp.workcenter')
    
    total_de_personas = fields.Float(copy=True,digits=(12, 2)) 
    horas_hombre_x_pieza = fields.Float(copy=True,digits=(12, 2))
    eficiencia_de_la_operacion = fields.Float(copy=True,digits=(12, 2))
    horas_hombre_total = fields.Float(copy=True,digits=(12, 2))
    precio_unitario = fields.Float(copy=True,digits=(12, 2))
    total = fields.Float(copy=True,digits=(12, 2))
    notas = fields.Text(copy=True,digits=(12, 2))
    hoja_de_proyecto = fields.Many2one('escenario_de_ventas.hoja_de_proyecto',copy=True,digits=(12, 2))

    @api.onchange('total_de_personas','horas_hombre_x_pieza','horas_hombre_total','precio_unitario','total','eficiencia_de_la_operacion')
    def _onchange_hoja_de_proyecto(self):
        for item in self:            
            if item.hoja_de_proyecto.piezas_por_dia_linea<=0:
                raise UserError(('El campo Piezas Por Dia Linea debe ser mayor a 0 \nrevise la sección \nESTIMACION DE LOS MATERIALES PARA EL PROYECTO'))
            if item.hoja_de_proyecto.eficiencia_del_lote<=0:
                raise UserError(('El campo Eficiencia Del Lote debe ser mayor a 0 \nrevise la sección \nESTIMACION DE LOS MATERIALES PARA EL PROYECTO'))
            if item.hoja_de_proyecto.costo_mo<=0:
                raise UserError(('El campo Costo Mo debe ser mayor a 0 \nrevise la sección \nESTIMACION DE LOS MATERIALES PARA EL PROYECTO'))
            if item.total_de_personas<0:
                raise UserError(('La cantidad de Personas no puede ser negativa, si no la tiene definida escriba el valor en 0'))
            try:
                item.precio_unitario=item.hoja_de_proyecto.costo_mo
                item.horas_hombre_x_pieza=(((item.total_de_personas*9.5)/item.hoja_de_proyecto.piezas_por_dia_linea)/item.hoja_de_proyecto.eficiencia_del_lote)*100
                item.horas_hombre_total=(item.horas_hombre_x_pieza*item.hoja_de_proyecto.total_piezas)/(item.eficiencia_de_la_operacion)*100
                item.total=item.horas_hombre_total*item.precio_unitario
            except:
                pass
            
#Total de Personas no puede menor a cero  

    @api.model
    def create(self, values):
        if values['mano_de_obra']<=0:
            raise UserError(('Por favor seleccione un centro de trabajo (Mano de obra)\nrevise la sección \nESTIMACION DE LOS MATERIALES PARA EL PROYECTO'))
        if values.get('eficiencia_de_la_operacion')<=0:
            raise UserError(('La eficiencia de operación no puede ser 0 \nrevise la sección \nESTIMACION DE LOS MATERIALES PARA EL PROYECTO'))
        if values.get('precio_unitario')<=0:
            raise UserError(('El precio unitario no puede ser 0 \nrevise la sección \nESTIMACION DE LOS MATERIALES PARA EL PROYECTO'))
        if values.get('total_de_personas')<=0:
            raise UserError(('El total de personas no puede ser 0 \nrevise la sección \nESTIMACION DE LOS MATERIALES PARA EL PROYECTO'))
        return super(Estimacion_De_Mano_De_Obra, self).create(values)




