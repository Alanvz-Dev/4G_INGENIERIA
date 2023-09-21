from odoo import _, api, fields, models



class Work_center(models.Model):
    _name = 'production_time.wcent_config'
    _sql_constraints = [('centro_de_produccion', 'unique(centro_de_produccion)', "No puede configurar un centro de producción más de una vez!")]
    antelacion = fields.Float(string='Días de Anticipación')
    centro_de_produccion = fields.Many2one('mrp.workcenter', string='Centro de Producción')
