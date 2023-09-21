from odoo import _, api, fields, models


class EscenarioDeVentas(models.Model):
    _name = 'escenario_de_ventas.escenario_de_ventas'
    _description = 'Escenario de Ventas'
    sale_id = fields.Many2one(comodel_name='sale.order', string='ID de Ventas')
    product_id = fields.Many2one(comodel_name='product.product', string='Producto')
    start_date = fields.Date(string='Fecha Programada')
    piezas_por_dia_linea = fields.Float(string='Piezas por Día',digits=(12, 2))
    costo_total = fields.Float(string='Costo Total',digits=(12, 2))
    cliente = fields.Many2one(comodel_name='res.partner', string='Cliente')
    state_hp = fields.Char(store=True,compute='_compute_state_hp', string='Estado de Hoja de Proyecto')
    hp = fields.Many2one(string='Hoja de Proyecto',related='sale_id.hoja_de_proyecto_origen',store=True)
    @api.depends('sale_id')
    def _compute_state_hp(self):
        for item in self:
            item.state_hp  =  item.sale_id.state_hp
    
    
    
    @api.onchange('piezas_por_dia_linea')
    def _onchange_escenario_de_ventas_lines(self):
        self.costo_total = self.piezas_por_dia_linea* self.sale_id.hoja_de_proyecto_origen.precio_por_pieza_mxn
        self.product_id=self.sale_id.product_id.id
        print(self)

    

    def return_pivot_views(self):
        escenario_de_ventas = self.env['escenario_de_ventas.escenario_de_ventas'].search([])
        for item in escenario_de_ventas:
            print('Anterior','\t',item.state_hp)
            item.state_hp = item.sale_id.state_hp
            print('Nuevo','\t',item.state_hp)
            print('\n')
        views = [
                 (self.env.ref('escenario_de_ventas.escenario_de_ventas_view_pivot').id, 'pivot'),
                 (self.env.ref('escenario_de_ventas.escenariode_ventas_view_tree').id, 'list'),
                #  (self.env.ref('mrp.mrp_capacidad_dia').id, 'graph'),
                #  (self.env.ref('mrp.mrp_capacidad_list_dia').id, 'list'),
                #  (self.env.ref('mrp.mrp_capacidad_prod_view_form_dia').id, 'form')
                ]
        return{
                'name': 'Escenario De Ventas',
                'view_type': 'form',
                "view_mode": "pivot",
                #"view_mode": "tree,form,graph",
                'view_id': False,
                "res_model": "escenario_de_ventas.escenario_de_ventas",
                'views': views,
                #'domain': [('id', 'in', invoices.ids)],
                'type': 'ir.actions.act_window',
            }
    



    
    @api.model
    def create(self, values):
        # CODE HERE
        if 'cliente' not in values:
            partner_id=self.sale_id.browse(values['sale_id']).partner_id.id
            values.update({'cliente':partner_id})
        return super(EscenarioDeVentas, self).create(values)