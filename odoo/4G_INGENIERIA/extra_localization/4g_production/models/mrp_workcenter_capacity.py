from odoo import _, api, fields, models


class WorkCenter(models.Model):
    _name = 'mrp.workcenter.capacity'
    _description = 'Capacidad de los centros de Producción'

    workcenter = fields.Many2one(comodel_name='mrp.workcenter')
    
    
    #tamanos_de_piezas = fields.Float(string='Tamaños de Piezas')
    calibre_li = fields.Float(string='EspesorLI(mm)',digits=(4,4))
    calibre_ls = fields.Float(string='EspesorLS(mm)',digits=(4,4))
    medida_maxima = fields.Float(string='Medida Máxima')
    minutos_por_doblez = fields.Float(string='Minutos Por Doblez')
    
    
    #material = fields.Many2one(comodel_name='mrp_workcenter_capacity.material')
    #velocidad_de_corte = fields.Float()
    
    
    # minutos_por_doblez = fields.Float(string='Minutos Por Doblez')
    # amperaje = fields.Float(string='Amperaje')
    # metro = fields.Float(string='Medida Lienal de Corte')
    # tiempo_de_corte_lineal = fields.Float(string='Tiempo Lienal de Corte')
    
    