from odoo import _, api, fields, models


class Laser(models.Model):
    _name = 'mrp.workcenter.laser'
    
    _description = 'Propiedas de la capacidad de producción de la máquina laser'

    workcenter = fields.Many2one(comodel_name='mrp.workcenter')
    
    #material = fields.Many2one(comodel_name='mrp_workcenter_capacity.material')
    calibre_li = fields.Many2one('capacidad_de_produccion.calibres_list', string='EspesorLI(mm)')
    calibre_ls = fields.Many2one('capacidad_de_produccion.calibres_list', string='Espesor(Ls)')
    # amperaje = fields.Float(string='Amperaje (A)')
    #velocidad_de_corte = fields.Float(string='Velocidad de Corte (F)')
    medida_lineal_de_corte = fields.Float(string='Medida Lineal de Corte (m)')
    tiempo_de_corte = fields.Float(string='Tiempo Lineal de Corte (Min.)')
    
    