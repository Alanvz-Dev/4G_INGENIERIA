from odoo import _, api, fields, models


class Cizalla(models.Model):
    _name = 'mrp.workcenter.cizalla'
    _description = 'Propiedas de la capacidad de producción de la cizalla'

    workcenter = fields.Many2one(comodel_name='mrp.workcenter') 
    
    
    

            
    
    
    calibre_li = fields.Many2one('capacidad_de_produccion.calibres_list', string='EspesorLI(mm)')
    calibre_ls = fields.Many2one('capacidad_de_produccion.calibres_list', string='Espesor(Ls)')
    medida_maxima_li=fields.Many2one('capacidad_de_produccion.madida_maxima', string='Perímetro LI(mm)')
    medida_maxima_ls=fields.Many2one('capacidad_de_produccion.madida_maxima', string='Perímetro LS(mm)')
    tiempo_de_corte = fields.Float(string='Tiempo de Corte (min.)')

    

 
    

    