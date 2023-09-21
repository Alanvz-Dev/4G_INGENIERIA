from odoo import _, api, fields, models


class Dobladora(models.Model):
    _name = 'mrp.workcenter.dobladora'
    
    _description = 'Propiedas de la capacidad de producción de las dobladoras'

    workcenter = fields.Many2one(comodel_name='mrp.workcenter')
    calibre_li = fields.Many2one('capacidad_de_produccion.calibres_list', string='Espesor LI(mm)')
    calibre_ls = fields.Many2one('capacidad_de_produccion.calibres_list', string='Espesor LS(mm)')
    medida_maxima_li=fields.Many2one('capacidad_de_produccion.madida_maxima', string='Perímetro LI(mm)')
    medida_maxima_ls=fields.Many2one('capacidad_de_produccion.madida_maxima', string='Perímetro LS(mm)')
    tiempo_de_corte = fields.Float(string='Tiempo por Doblez (min.)')

    
    
