from odoo import _, api, fields, models
from datetime import datetime


class MRP(models.TransientModel):
    _name = 'wizard.reporte_diario'
    _description = 'Reporte Diario de Producción Wizard'
    fecha = fields.Date(string='Fecha:', default=datetime.today())
    centro_de_trabajo = fields.Many2many('mrp.workcenter')

    def ver_reporte_diario(self):
        fecha_i = self.fecha+" 00:00:00.000"
        fecha_f = self.fecha+" 23:59:59.000"
        ordenes_de_trabajo = self.env['mrp.workorder'].search([('production_date', '>=', fecha_i),('production_date', '<=', fecha_f), ('workcenter_id', 'in', self.centro_de_trabajo.ids)])
        views = [
            (self.env.ref('mrp.mrp_production_workcenter_tree_view_inherit').id, 'list'),
            (self.env.ref('mrp.mrp_production_workcenter_form_view_inherit').id, 'form'),
        ]
        return{
            'name': 'Reporte del '+self.fecha,
            'view_type': 'form',
            "view_mode": "tree,form",
            "res_model": "mrp.workorder",
            'views': views,
            'domain': [('id', 'in', ordenes_de_trabajo.ids)],
            'type': 'ir.actions.act_window',
        }