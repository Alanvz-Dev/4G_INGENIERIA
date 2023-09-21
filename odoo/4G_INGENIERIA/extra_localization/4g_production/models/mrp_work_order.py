from odoo import _, api, fields, models


class ModuleName(models.Model):
    _inherit = 'mrp.workorder'


    bom_line_ids = fields.One2many(related='production_id.bom_id.bom_line_ids')
    imagen_referencia = fields.Html(compute='_compute_imagen_referencia', string='')
    qty_rack = fields.Char(compute='_compute_qty_rack', string='Cantidad Por Rack') 
    
    @api.one
    @api.depends('production_id')
    def _compute_qty_rack(self):
        self.qty_rack=self.qty_production*self.production_id.product_qty
        
    @api.depends('production_id')
    def _compute_imagen_referencia(self):
        self.imagen_referencia=self.production_id.bom_id.imagen_de_referencia





                                        
    
