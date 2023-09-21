# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError,UserError


class Escenario_De_Ventas(models.Model):
    _name = 'escenario_de_ventas.hoja_de_proyecto'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _description = 'Hoja de Proyecto'

    @api.model
    def _obtener_categorias_por_defecto(self):
        return self.env['product.category'].search([('name', 'in', ['ACEROS', 'PERIFERICOS', 'MATERIALES IMPORTADOS'])]).ids
    # Renombrar mano_de_obra_ids
    nombre_de_proyecto = fields.Char(copy=True)
    name = fields.Char(readonly=True, required=True,copy=False, default='HPXXXX')
    active = fields.Boolean(default=True,copy=True)
    cotizacion_rfq = fields.Char(copy=True)
    cierre_de_venta_de_orden_de_compra = fields.Date(copy=True)
    fecha_de_entrega = fields.Datetime(copy=True)
    proyectista_contacto = fields.Many2one(comodel_name='res.users',copy=True)
    crm_lead_id = fields.Many2many('crm.lead',copy=True)
    largo_m = fields.Float(digits=(12, 2))
    ancho_m = fields.Float(digits=(12, 2))
    alto_m = fields.Float(digits=(12, 2))
    largo_in = fields.Float(digits=(12, 2))
    ancho_in = fields.Float(digits=(12, 2))
    alto_in = fields.Float(digits=(12, 2))
    actualizar_precios = fields.Selection(string='Actualizar Precios al cambiar la cantidad de Piezas', selection=[('yes', 'SI'), ('no', 'NO')])
    largo_cm = fields.Float(digits=(12, 2))
    ancho_cm = fields.Float(digits=(12, 2))
    alto_cm = fields.Float(digits=(12, 2))
    largo_mm = fields.Float(digits=(12, 2))
    ancho_mm = fields.Float(digits=(12, 2))
    alto_mm = fields.Float(digits=(12, 2))
    medida_principal = fields.Selection(selection=[('cm', 'Centímetros'), ('m', 'Metros'), ('in', 'Pulgadas'), ('mm', 'Milímetros')],copy=True)
    piezas_por_dia_linea = fields.Float(digits=(12, 2))
    eficiencia_del_lote = fields.Float(digits=(12, 2))
    costo_mo = fields.Float(digits=(12, 2))
    total_piezas = fields.Float(digits=(12, 2))
    materiales = fields.One2many('escenario_de_ventas.materiales', 'hoja_de_proyecto',copy=True)
    otros_gastos_fletes_maq = fields.One2many('escenario_de_ventas.otros_gastos_fletes_maq', 'hoja_de_proyecto',copy=True)
    mano_de_obra_ids = fields.One2many('escenario_de_ventas.estimacion_de_mano_de_obra', 'hoja_de_proyecto',copy=True)
    filtro_de_categorias = fields.Many2many('product.category', default=_obtener_categorias_por_defecto,copy=True)
# Resumen
    costo_total = fields.Float(digits=(12, 2))
    margenes = fields.Float(digits=(12, 2))
    otros_gastos = fields.Float(digits=(12, 2))
    precio_proyecto_mxn = fields.Float(compute='_compute_precio_proyecto_mxn',store=True,copy=True)
    precio_por_pieza_mxn = fields.Float(digits=(12, 2))
    precio_proyecto_usd = fields.Float(digits=(12, 2))
    precio_por_pieza_usd = fields.Float(digits=(12, 2))
    tipo_de_cambio_usd = fields.Float(digits=(12, 2))
    precio_usd = fields.Float(digits=(12, 2))
    margen_materiales_ = fields.Float(digits=(12, 2))
    margen_mano_de_obra = fields.Float(digits=(12, 2))
    margen_otros_gastos = fields.Float(digits=(12, 2))
    margen_precio_proyecto = fields.Float(digits=(12, 2))
    margen_precio_por_pieza = fields.Float(digits=(12, 2))
    presupuesto_aceros = fields.Float(digits=(12, 2))
    presupuesto_perifericos = fields.Float(digits=(12, 2))
    presupuesto_importaciones = fields.Float(digits=(12, 2))
    presupuesto_fletes_y_otros = fields.Float(digits=(12, 2))
    presupuesto_mano_de_obra = fields.Float(digits=(12, 2))
    aceros = fields.Float(compute='_onchange_materiales_filtro_de_categorias')
    materiales_importados = fields.Float(compute='_onchange_materiales_filtro_de_categorias')
    perifericos = fields.Float(compute='_onchange_materiales_filtro_de_categorias')
    otros_productos = fields.Float(compute='_onchange_materiales_filtro_de_categorias')
    total_productos = fields.Float(compute='_onchange_materiales_filtro_de_categorias')
    total_mano_de_obra = fields.Float(compute='_onchange_mano_de_obra_ids')
    total_otros_gatos_fletes_y_maquilas = fields.Float(compute='_onchange_otros_gastos_fletes_maq', string="Total Otros Gsatos Fletes Y Maquilas")
    image = fields.Binary()
    total_monto_materiales = fields.Float(digits=(12, 2))
    total_monto_mano_de_obra = fields.Float(compute='_onchange_mano_de_obra_ids')
    total_monto_otros_gastos = fields.Float(compute='_onchange_otros_gastos_fletes_maq')
    total_con_margen = fields.Float(compute='_compute_total_con_margen', string='Total')
    total_sin_margen = fields.Float(compute='_compute_total_con_margen', string='Subtotal')
    peso_total = fields.Float(digits=(12, 2))
    price_list = fields.Many2one(comodel_name='product.pricelist')
    usd_or_mxn = fields.Boolean(compute='_compute_usd_or_mxn')
    utilidad_por_pieza = fields.Float(digits=(12, 2))
    utilidad_total = fields.Float(digits=(12, 2))
    presupuesto_de_venta_creado = fields.Boolean(default=False)
    presupuesto_de_proyecto_creado = fields.Boolean(default=False)
    precio_ptr = fields.Float(digits=(12, 2))
    precio_lamina_placa = fields.Float(digits=(12, 2))
    precios_solidos = fields.Float(digits=(12, 2))
    filtro_de_categorias_ptr = fields.Many2many('product.category', 'filtro_ptr')
    filtro_de_categorias_lamina_placa = fields.Many2many('product.category', 'filtro_lamina_placa')
    filtro_de_categorias_solidos = fields.Many2many('product.category', 'filtro_solidos')
    nombre_de_cliente = fields.Many2one(comodel_name='res.partner',copy=True)
    familia_de_productos = fields.Many2one(comodel_name='product.category',copy=True)
    material_x_pieza = fields.Float(compute='_compute_material_x_pieza', string='Monto de Material por Pieza',digits=(12, 2))
    precio_por_pieza_mxn_sin_margen = fields.Float(compute='_compute_precio_por_pieza_mxn_sin_margen', string='Costo Por Pieza Mxn',digits=(12, 2))
    pedido_de_venta = fields.Many2one('sale.order', string='Pedido de Venta Asociado')
    proyecto_asociado = fields.Many2one('project.project', string='Proyecto Asociado')
    presupuesto_asociado = fields.Many2one('crossovered.budget.project', string='Presupuesto Asociado')
    @api.depends('precio_por_pieza_mxn')
    def _compute_precio_por_pieza_mxn_sin_margen(self):
        if self.total_piezas>0:
            self.precio_por_pieza_mxn_sin_margen = (self.total_sin_margen/self.total_piezas or 0)

    @api.depends('total_productos')
    def _compute_material_x_pieza(self):
        if self.total_piezas>0:
            self.material_x_pieza = (self.total_productos/self.total_piezas or 0)

    mano_de_obra_x_pieza = fields.Float(compute='_compute_mano_de_obra_x_pieza', string='Monto de Mano de Obra por Pieza',digits=(12, 2))

    @api.depends('total_mano_de_obra')
    def _compute_mano_de_obra_x_pieza(self):
        if self.total_mano_de_obra > 0 or self.total_piezas >0:
            self.mano_de_obra_x_pieza = (self.total_mano_de_obra/self.total_piezas or 0)

    otr_gast_maq_x_pieza = fields.Float(compute='_compute_otr_gast_maq_x_pieza_x_pieza', string='Monto de Otros Gastos Fletes y Maquilas por Pieza',digits=(12, 2))

    @api.depends('total_otros_gatos_fletes_y_maquilas')
    def _compute_otr_gast_maq_x_pieza_x_pieza(self):
        if self.total_otros_gatos_fletes_y_maquilas > 0 or self.total_piezas >0:            
            self.otr_gast_maq_x_pieza = (
                self.total_otros_gatos_fletes_y_maquilas/self.total_piezas or 0)

    @api.depends('price_list')
    def _compute_usd_or_mxn(self):
        if self.price_list.currency_id.name == 'USD':
            self.usd_or_mxn = True
        elif self.price_list.currency_id.name == 'MXN':
            self.usd_or_mxn = False
        pass

    @api.one
    @api.depends('price_list', 'tipo_de_cambio_usd', 'total_monto_materiales', 'total_monto_mano_de_obra', 'total_monto_otros_gastos', 'total_productos', 'total_mano_de_obra', 'total_otros_gatos_fletes_y_maquilas')
    def _compute_total_con_margen(self):
        self.total_sin_margen = self.total_productos + \
            self.total_mano_de_obra+self.total_otros_gatos_fletes_y_maquilas
        self.total_con_margen = self.total_monto_materiales + \
            self.total_monto_mano_de_obra+self.total_monto_otros_gastos




    @api.model
    def create(self, values):
        # CODE HERE
        # Si existen campos de solo lectura el método create no los tomará en cuenta
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'escenario_de_ventas.hoja_de_proyecto') or _('New')
        rec = super(Escenario_De_Ventas, self).create(values)
        if 'active_id' in self._context:
            rec.crm_lead_id = [(4, self._context['active_id'])]
        return rec



    @api.multi
    def write(self, values):
        print(self)
        if self.pedido_de_venta:
            product = self.env['product.product'].search(
                [('origen_hoja_de_proyecto', 'in', [self.id])])
            if len(product) > 1:        
                raise ValidationError("Solo puede existir un producto por hoja de proyecto. Vaya al boton de Producto y asegurese que solo tenga un registro.")
            
            if 'precio_por_pieza_mxn' in values and 'total_sin_margen' in values and  'total_piezas' in values:                
                product.lst_price = values['precio_por_pieza_mxn']
                product.standard_price = values['precio_por_pieza_mxn']
                product.cost_product=values['precio_por_pieza_mxn']
                sale_order_line = self.pedido_de_venta.order_line.search(
                    [('order_id', 'in', [self.pedido_de_venta.id]), ('product_id', 'in', [product.id])])
                if not sale_order_line:
                    raise UserError("El producto  %s falta la línea del pedido de venta %s "%(product.name,self.pedido_de_venta.name))
                sale_order_line.purchase_price=values['total_sin_margen']/values['total_piezas']
                sale_order_line.price_unit=values['precio_por_pieza_mxn']
                sale_order_line.product_uom_qty=values['total_piezas']
                print(sale_order_line)
                print(product)
                # CODE HERE
                if self.pedido_de_venta:
                    escenario_de_ventas=self.env['escenario_de_ventas.escenario_de_ventas'].search([('sale_id','in',self.pedido_de_venta.ids)])
                    for item in escenario_de_ventas:
                        item.costo_total=item.piezas_por_dia_linea*values['precio_por_pieza_mxn']                
        return super(Escenario_De_Ventas, self).write(values)


    product_count = fields.Float(compute='_compute_product_count')
    def _compute_product_count(self):
        for record in self:
            x=self.env['product.product'].search_count([('origen_hoja_de_proyecto', 'in', [self.id])])
            record.product_count = self.env['product.product'].search_count([('origen_hoja_de_proyecto', 'in', [self.id])])
            print(x)
    

    def producto_creado(self):        
        product = self.env['product.product'].search(
            [('origen_hoja_de_proyecto', 'in', [self.id])])  
        views = [                                         
                     (self.env.ref('product.product_product_tree_view').id, 'list'),
                     (self.env.ref('product.product_normal_form_view').id, 'form')]
        return{
                    'name': 'PODUCTO',
                    'view_type': 'form',
                    "view_mode": "tree,form",
                    #"view_mode": "tree,form,graph",
                    'view_id': False,
                    "res_model": "product.product",
                    'views': views,
                    'domain': [('id', 'in', product.ids)],
                    'type': 'ir.actions.act_window',
                }


                    
    @api.onchange('piezas_por_dia_linea', 'eficiencia_del_lote', 'costo_mo')
    def _onchange_(self):
        self.mano_de_obra_ids._onchange_hoja_de_proyecto()
        self._onchange_mano_de_obra_ids()

    @api.one
    @api.depends('mano_de_obra_ids', 'margen_mano_de_obra')
    def _onchange_mano_de_obra_ids(self):
        total = 0.0
        for line in self.mano_de_obra_ids:
            total = total+line.total
        self.total_mano_de_obra = total
        self.total_monto_mano_de_obra = (
            total/(1-self.margen_mano_de_obra/100))
        
    @api.one
    @api.depends('otros_gastos_fletes_maq', 'margen_otros_gastos')
    def _onchange_otros_gastos_fletes_maq(self):
        total = 0.0
        for line in self.otros_gastos_fletes_maq:
            total = total+line.total
        self.total_otros_gatos_fletes_y_maquilas = total
        self.total_monto_otros_gastos = (
            total/(1-self.margen_otros_gastos/100))

    @api.one
    @api.depends('materiales', 'filtro_de_categorias', 'margen_materiales_')
    def _onchange_materiales_filtro_de_categorias(self):
        aceros_categoria_ids = []
        perifericos_categoria_ids = []
        materiales_importados_categoria_ids = []
        aceros = 0.0
        materiales_importados = 0.0
        perifericos = 0.0
        otros_productos = 0.0
        count = 0
        peso_total = 0.0
        for categoria in self.filtro_de_categorias:
            if count == 0:
                aceros_categoria_ids = self.get_category_ids(categoria)
            if count == 1:
                perifericos_categoria_ids = self.get_category_ids(categoria)
            if count == 2:
                materiales_importados_categoria_ids = self.get_category_ids(
                    categoria)
            count = count+1

        for material in self.materiales:
            peso_total = peso_total+material.peso_total
            if material.categoria.id in aceros_categoria_ids:
                aceros = aceros+material.total
            elif material.categoria.id in perifericos_categoria_ids:
                materiales_importados = materiales_importados+material.total
            elif material.categoria.id in materiales_importados_categoria_ids:
                perifericos = perifericos+material.total
            else:
                otros_productos = otros_productos+material.total

        self.aceros = aceros
        self.peso_total = peso_total
        self.materiales_importados = materiales_importados
        self.perifericos = perifericos
        self.otros_productos = otros_productos
        self.total_productos = self.aceros+self.materiales_importados + \
            self.perifericos+self.otros_productos

        self.total_monto_materiales = (
            self.total_productos/(1-self.margen_materiales_/100))

    def get_category_ids(self, category):
        return self.env['product.category'].search([('id', 'child_of', category.id)]).ids

    @api.onchange('cierre_de_venta_de_orden_de_compra')
    def _onchange_cierre_de_venta_de_orden_de_compra(self):
        try:
            self.cierre_de_venta_de_orden_de_compra = datetime.strptime(
                self.cierre_de_venta_de_orden_de_compra, "%Y-%M-%d")+timedelta(days=15)
        except:
            print("")

    @api.onchange('largo_m', 'ancho_m', 'alto_m', 'largo_in', 'ancho_in', 'alto_in', 'largo_cm', 'ancho_cm', 'alto_cm', 'largo_mm', 'ancho_mm', 'alto_mm')
    def _onchange_dimensiones(self):

        if self.medida_principal == 'm':
            self.largo_cm = self.largo_m*100
            self.largo_in = self.largo_m*39.37
            self.largo_mm = self.largo_m*1000

            self.ancho_cm = self.ancho_m*100
            self.ancho_in = self.ancho_m*39.37
            self.ancho_mm = self.ancho_m*1000

            self.alto_cm = self.alto_m*100
            self.alto_in = self.alto_m*39.37
            self.alto_mm = self.alto_m*1000

        elif self.medida_principal == 'cm':
            self.largo_in = self.largo_cm/2.54
            self.largo_m = self.largo_cm/100
            self.largo_mm = self.largo_cm*10

            self.ancho_in = self.ancho_cm/2.54
            self.ancho_m = self.ancho_cm/100
            self.ancho_mm = self.ancho_cm*10

            self.alto_in = self.alto_cm/2.54
            self.alto_m = self.alto_cm/100
            self.alto_mm = self.alto_cm*10

        elif self.medida_principal == 'in':
            self.largo_cm = self.largo_in*2.54
            self.largo_m = self.largo_in/39.37
            self.largo_mm = self.largo_in*25.4

            self.ancho_cm = self.ancho_in*2.54
            self.ancho_m = self.ancho_in/39.37
            self.ancho_mm = self.ancho_in*25.4

            self.alto_cm = self.alto_in*2.54
            self.alto_m = self.alto_in/39.37
            self.alto_mm = self.alto_in*25.4

        elif self.medida_principal == 'mm':
            self.largo_cm = self.largo_mm/10
            self.largo_in = self.largo_mm/25.4
            self.largo_m = self.largo_mm/1000

            self.ancho_cm = self.ancho_mm/10
            self.ancho_in = self.ancho_mm/25.4
            self.ancho_m = self.ancho_mm/1000

            self.alto_cm = self.alto_mm/10
            self.alto_in = self.alto_mm/25.4
            self.alto_m = self.alto_mm/1000

    def crear_presupuesto_de_ventas(self):
        if self.pedido_de_venta:
            raise ValidationError(
                "Ya existe un pedido de venta asociado a la Hoja de Proyecto.")
        precio = 0
        if self._compute_usd_or_mxn():
            precio = self.precio_por_pieza_usd
        elif not self._compute_usd_or_mxn():
            precio = self.precio_por_pieza_mxn
        product_vals = {
            "states": "draft",
            "active": True,
            "sale_ok": True,
            "purchase_ok": True,
            "type": "product",
            "categ_id": self.familia_de_productos.id,
            "list_price": precio,
            'route_id': 6,
            # self.env['res.company']._company_default_get('account.invoice').id,
            "company_id": 1,
            "uom_id": 50,
            "uom_po_id": 50,
            "purchase_requisition": 'rfq',
            "route_ids": [[6, False, []]],
            "produce_delay": 0,
            "sale_delay": 0,
            "responsible_id": 1,
            "origen_hoja_de_proyecto": self.id,
            "tracking": "none",
            "property_stock_production": 7,
            "property_stock_inventory": 5,
            "taxes_id": [[6, False, [2]]],
            "supplier_taxes_id": [[6, False, [10]]],
            "split_method": "equal",
            "invoice_policy": "delivery",
            "service_type": "manual",
            "service_tracking": "no",
            "expense_policy": "no",
            "purchase_method": "receive",
            "sale_line_warn": "no-message",
            "purchase_line_warn": "no-message",
            "name":  self.nombre_de_proyecto,
            "cost_product": precio,
            "standard_price": precio,
            "weight": self.peso_total,
            "volume": self.alto_m*self.ancho_m*self.largo_m,
            "service_policy": "delivered_manual",

        }
        product = self.env['product.template'].create(product_vals)
        print(product.id)
        # self.env.cr.commit()

        pedido_de_venta_vals = {
            "opportunity_id": self.crm_lead_id.id,
            "partner_id": self.nombre_de_cliente.id,
            "note": "",
            "hoja_de_proyecto_origen": self.id,
            "warehouse_id": 1,
            "picking_policy": "direct",
            "user_id": self._uid,
            'pricelist_id': self.price_list.id,
            # self.env['res.company']._company_default_get('account.invoice').id,
            'team_id': False,
            "company_id": 1,
            "date_order": datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S"),
            "order_line": [
                [
                    0,
                    'virtual_689',
                    {
                        "sequence": 10,
                        "product_uom_qty": self.total_piezas,
                        "price_unit": precio,
                        "discount": 0,
                        "customer_lead": 0,
                        "product_id": product.product_variant_id.id,
                        "tracking": "none",
                        "name": product.name,
                        "product_uom": 50,
                        "analytic_tag_ids": [[6, False, []]],
                        "purchase_price": self.total_sin_margen/self.total_piezas,
                        "tax_id": [[6, False, [2]]],
                    },
                ]
            ]
        }

        orden_de_venta = self.env['sale.order'].create(pedido_de_venta_vals)
        self.pedido_de_venta = (orden_de_venta.id, 0, orden_de_venta.ids)

    def crear_presupuesto_de_proyecto(self):
        if not self.pedido_de_venta:
            raise ValidationError(
                "No existe un pedido de venta asociado a la Hoja de Proyecto.")
        if self.pedido_de_venta:
            product = self.env['product.product'].search([('origen_hoja_de_proyecto', 'in', [self.id])])
            if not product:
                raise UserError(('Por favor Asocie la hoja de proyecto al Producto.'))

            if not len(product)>=1:
                raise UserError(('Verifique que exista solo un producto con origen en esta hoja de proyecto.'))
            product_res = self.pedido_de_venta.order_line.search([('order_id', 'in', [self.pedido_de_venta.id]), ('product_id', 'in', [product.id])]) 
            nombre_producto = product_res.product_id.name
            proyecto = self.env['project.project'].create({'user_id': False, 'allow_timesheets': False, 'plantilla': 'platillafabricacion', 'name': nombre_producto, 'alias_name': False})
            self.proyecto_asociado = (proyecto.id, 0, proyecto.ids)
            cuenta_analitica = proyecto.analytic_account_id
            ultima_tasa_de_cambio = self.env['res.currency.rate'].search(
                [], order='create_date desc', limit=1)
            # Creacion de Presupuesto
            budget = self.env['crossovered.budget.project'].create({
                'name': cuenta_analitica.id,
                'tasa_usd': ultima_tasa_de_cambio.id or False,
                'creating_user_id': self.env.user.id,
                'state': 'draft',
                'company_id': 1
            })

            self.presupuesto_asociado = (budget.id, 0, budget.ids)

            budget_lines = self.env['crossovered.budget.project.lines.usd']
            aceros_line = {
                'crossovered_budget_id': budget.id,
                'responsible_employee': False,
                'general_budget_id': 1,
                'currency_line': 34,
                'planned_amount': self.aceros*-1,
            }
            budget_lines.create(aceros_line)

            perifericos_line = {
                'crossovered_budget_id': budget.id,
                'responsible_employee': False,
                'general_budget_id': 2,
                'currency_line': 34,
                'planned_amount': self.materiales_importados*-1,
            }

            budget_lines.create(perifericos_line)

            importaciones_line = {
                'crossovered_budget_id': budget.id,
                'responsible_employee': False,
                'general_budget_id': 5,
                'currency_line': 34,
                'planned_amount': self.perifericos*-1,
            }

            budget_lines.create(importaciones_line)

            otros_productos_line = {
                'crossovered_budget_id': budget.id,
                'responsible_employee': False,
                'general_budget_id': 8,
                'currency_line': 34,
                'planned_amount': self.otros_productos*-1,
            }

            budget_lines.create(otros_productos_line)

            fletes_maquilas_line = {
                'crossovered_budget_id': budget.id,
                'responsible_employee': False,
                'general_budget_id': 6,
                'currency_line': 34,
                'planned_amount': self.total_otros_gatos_fletes_y_maquilas*-1,
            }

            budget_lines.create(fletes_maquilas_line)

            ventas_line = {
                'crossovered_budget_id': budget.id,
                'responsible_employee': False,
                'general_budget_id': 7,
                'currency_line': 34,
                'planned_amount': self.total_con_margen,
            }
            budget_lines.create(ventas_line)
            mano_de_obra_line = {
                'crossovered_budget_id': budget.id,
                'responsible_employee': False,
                'general_budget_id': 3,
                'currency_line': 34,
                'planned_amount': self.total_monto_mano_de_obra*-1,
            }
            budget_lines.create(mano_de_obra_line)

    def actualizar_presupuesto(self):

        res = self.presupuesto_asociado.crossovered_budget_line_usd.filtered(lambda r: r.general_budget_id.id == 1)
        if res:res.planned_amount = self.aceros*-1

        res = self.presupuesto_asociado.crossovered_budget_line_usd.filtered(lambda r: r.general_budget_id.id == 2)
        if res:res.planned_amount = self.materiales_importados*-1

        res = self.presupuesto_asociado.crossovered_budget_line_usd.filtered(lambda r: r.general_budget_id.id == 5)
        if res:res.planned_amount = self.perifericos*-1

        res = self.presupuesto_asociado.crossovered_budget_line_usd.filtered(lambda r: r.general_budget_id.id == 8)
        if res:res.planned_amount = self.otros_productos*-1

        res = self.presupuesto_asociado.crossovered_budget_line_usd.filtered(lambda r: r.general_budget_id.id == 6)
        if res:res.planned_amount = self.total_otros_gatos_fletes_y_maquilas*-1

        res = self.presupuesto_asociado.crossovered_budget_line_usd.filtered(lambda r: r.general_budget_id.id == 7)
        if res:res.planned_amount = self.total_con_margen        
        
        res = self.presupuesto_asociado.crossovered_budget_line_usd.filtered(lambda r: r.general_budget_id.id == 3)
        if res:res.planned_amount = self.total_monto_mano_de_obra*-1



    @api.multi
    def write(self, vals):
        # Agregar codigo de validacion aca
        res = super().write(vals)
        if 'total_piezas' in vals:
            self.actualizar_presupuesto()
        return res


    def actualizar_precios_de_productos(self):
        for item in self.materiales:
            item._onchange_product_id()

    @api.onchange('total_piezas')
    def _onchange_total_piezas(self):
        self._onchange_mano_de_obra_ids()
        self.mano_de_obra_ids._onchange_hoja_de_proyecto()
        self._onchange_()
        self._onchange_otros_gastos_fletes_maq()
        for item in self.materiales:
            item._onchange_product_id()

        self._compute_total_con_margen()
        self._onchange_materiales_filtro_de_categorias()



    
    @api.depends('total_con_margen')
    def _compute_precio_proyecto_mxn(self):
        total_con_margen=self.total_con_margen
        self.precio_proyecto_mxn = total_con_margen
        print(self.precio_proyecto_mxn)
        if self.precio_proyecto_mxn > 0 and self.total_piezas > 0:
            self.precio_por_pieza_mxn = self.precio_proyecto_mxn/self.total_piezas
        print(self.precio_proyecto_mxn)
        if total_con_margen > 0 and self.total_sin_margen > 0:
            self.utilidad_total = total_con_margen-self.total_sin_margen
        print(self.precio_proyecto_mxn)
        if self.utilidad_total > 0 and self.total_piezas > 0:
            self.utilidad_por_pieza = self.utilidad_total/self.total_piezas
        print(self.precio_proyecto_mxn)
        if self.precio_proyecto_mxn > 0 and total_con_margen > 0 and self.price_list.currency_id.name == 'USD' and self.tipo_de_cambio_usd > 0:
            self.precio_proyecto_usd = self.precio_proyecto_mxn/self.tipo_de_cambio_usd
            self.precio_por_pieza_usd = self.precio_por_pieza_mxn/self.tipo_de_cambio_usd
            print(self.precio_proyecto_mxn)
        elif self.precio_proyecto_mxn > 0 and self.price_list.currency_id.name == 'MXN':
            self.precio_proyecto_mxn=total_con_margen
            print(self.precio_proyecto_mxn)            
        print(self.precio_proyecto_mxn)
        print(self.precio_proyecto_mxn)
    
# ¿Habrá alguna ruta?
# ¿Ubicaciones de contrapartida?

# {'partner_id': 1733, 'note': '', 'warehouse_id': 1, 'picking_policy': 'direct', 'user_id': 423, 'team_id': 15, 'company_id': 1, 'date_order': '2021-06-28 21:28:03', 'chrysler_addenda': False, 'fecha_rfq': False, 'fecha_oc': False, 'partner_invoice_id': 1733, 'partner_shipping_id': 1733, 'date_from_lead': False, 'validity_date': False, 'pricelist_id': 1, 'payment_term_id': False, 'order_line': [[0, 'virtual_750', {'sequence': 10, 'product_uom_qty': 1, 'price_unit': 28515.84, 'discount': 0, 'customer_lead': 0, 'product_id': 65123, 'tracking': 'none', 'lot_id': False, 'layout_category_id': False, 'name': '[00001 3056425+MAC30874] 3056425+MAC30874', 'product_uom': 35, 'analytic_tag_ids': [[6, False, []]], 'route_id': False, 'purchase_price': 1, 'no_parte': False, 'line_item': False, 'tax_id': [[6, False, [2]]]}]], 'incoterm': False, 'client_order_ref': False, 'analytic_account_id': False, 'fiscal_position_id': False, 'origin': False, 'forma_pago': False, 'methodo_pago': False, 'uso_cfdi': False, 'codigo_envio': False, 'orden_compra': False, 'requicision_liberacion': False, 'fca_tipodocumento': False, 'no_compra': False}

    def actualizar_precios_de_productos_categoria(self):
        for line in self.materiales:
            if not line.personalizar_registro:
                if line.categoria.id in self.filtro_de_categorias_ptr.ids:
                    line.precio_unitario = line.product_id.weight * self.precio_ptr
                if line.categoria.id in self.filtro_de_categorias_lamina_placa.ids:
                    line.precio_unitario = line.product_id.weight * self.precio_lamina_placa
                if line.categoria.id in self.filtro_de_categorias_solidos.ids:
                    line.precio_unitario = line.product_id.weight * self.precios_solidos
                line._onchange_product_id()

    @api.constrains('active')
    def _archive(self):
        product = self.env['product.product'].search([('origen_hoja_de_proyecto','in',self.ids)])
        if not self.active:        
            for item in self:
                for pedido in item.pedido_de_venta:
                    pedido.active=False
                for proyecto in item.proyecto_asociado:
                    proyecto.active=False
                for presupuesto in item.presupuesto_asociado:
                    presupuesto.active=False
                for prod in product:
                    prod.active=False
        elif not self.active:
            for item in self:
                for pedido in item.pedido_de_venta:
                    pedido.active=True
                for proyecto in item.proyecto_asociado:
                    proyecto.active=True
                for presupuesto in item.presupuesto_asociado:
                    presupuesto.active=True
                for prod in product:
                    prod.active=True
            self.active=True