from odoo import _, api, fields, models


class WorkCenter(models.Model):
    _inherit = 'mrp.workcenter'
    _description = 'Centros de Producción'
    work_center_capacity_pantografo_lines = fields.One2many(comodel_name='mrp.workcenter.pantografo', inverse_name='workcenter')
    work_center_capacity_cizalla_lines = fields.One2many(comodel_name='mrp.workcenter.cizalla', inverse_name='workcenter')
    work_center_capacity_dobladora_lines = fields.One2many(comodel_name='mrp.workcenter.dobladora', inverse_name='workcenter')
    work_center_capacity_laser_lines = fields.One2many(comodel_name='mrp.workcenter.laser', inverse_name='workcenter')
    tipo_de_maquina = fields.Selection(string='Tipo de Máquina', selection=[('cizalla', 'Cizalla'), ('dobladora', 'Dobladora'), ('pantografo', 'Pantografo'), ('laser', 'Láser')])
    habilitar_capacidad_de_produccion = fields.Boolean(string='Habilitar Capacidad de Producción')
    
    
    objetivo_estandar = fields.Float(string='Objetivo Estandar de Tiempo (min.)')
