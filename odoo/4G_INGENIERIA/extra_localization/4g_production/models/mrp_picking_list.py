from email.policy import default
from os import unlink
from odoo.exceptions import UserError
from odoo import _, api, fields, models
import math


class PickingList(models.TransientModel):
    _name = 'mrp.picking_list_wizard'
    _description = 'Picking List'
    date_from = fields.Datetime(string='Desde:')
    date_to = fields.Datetime(string='Al:')

    @api.multi
    def get_mos(self):
        configurations = self.env['mrp.picking_list_settings'].search([]).mapped('rutas').ids
        domain = [('date_planned_start', '>=', self.date_from), ('date_planned_start',
                                                                 '<=', self.date_to), ('state', 'in', ['planned', 'confirmed']),
                  ('routing_id', 'in', configurations)]
        action_id = self.env.ref('mrp.picking_list_action').read()[0]
        action_id.update({'domain': domain})
        return action_id


class Mrp(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def search_mo_origin(self, mrp_ids, product_id):
        ids = []
        mos = self.search([('id', 'in', mrp_ids)])
        for mo in mos:
            recs = mo.move_raw_ids.search([('raw_material_production_id', 'in', [
                                          mo.id]), ('product_id', 'in', [product_id])])
            ids.append(recs.raw_material_production_id.id)
        return ids

    @api.multi
    def check_availability(self, product_id, location_ids):
        # agrupar por producto search_read
        stock_quant_prod = self.env['stock.quant'].search(
            [('location_id', 'in', location_ids), ('product_id', 'in', [product_id])])
        return {'quantity': sum(stock_quant_prod.mapped('quantity')), 'reserved_quantity': sum(stock_quant_prod.mapped('reserved_quantity'))}


    @api.multi
    def get_location_ids(self, product_id, mo_ids):
        return self.search([('id', 'in', mo_ids), ('move_raw_ids.product_id', 'in', [product_id])]).mapped('routing_id').mapped('location_id').ids

    @api.one
    def multiple_assign(self):
        self.action_assign()

    @api.one
    def multiple_plan(self):
        self.button_plan()


    def compute_qty_available_prod_stock(self,mrp_obj,product_id):
        # Prod/Stock    
        location_default = 22
        quant = self.check_availability(product_id, [location_default])
        return quant['quantity']-quant['reserved_quantity']


    def get_routing_ids(self,production_ids):
        routing_ids = []
        groupped_ids =self.env['mrp.production'].read_group([('id', 'in',production_ids)], ['routing_id'], ['routing_id'], 0, None, False, False)
        for item in groupped_ids:
            routing_ids.append(item['routing_id'][0])        
        return routing_ids

    def get_production_ids_by_routing_id(self,routing_ids,production_ids):
        return self.search([('id','in',production_ids),('routing_id','in',routing_ids)])




    @api.multi
    def generate_picking_list(self):
        created_ids = []
        configurations = self.env['mrp.picking_list_settings'].search([])
        rounting = self.get_routing_ids(self.ids)
        for config in configurations:                     
            production_ids = self.get_production_ids_by_routing_id(config.rutas.ids,self.ids)
            if production_ids:        
                summary = self.env['mrp.picking_list_summary']
                res = summary.create({'entrega': self.env.uid,
                                     'recibe': False,
                                      'production_ids': [(6, 0, production_ids.ids)],
                                    #   'routing_id':False,
                                      'configuration_id': config.id,
                                      #   Configurations
                                      'location_id': config.location_id.id,
                                      'location_dest_id': config.location_dest_id.id,
                                      'move_type': config.move_type,
                                      'company_id': config.company_id.id,
                                      'picking_type_id': config.picking_type_id.id,
                                      })        
                ids = production_ids.mapped('move_raw_ids')
                stock_move = self.env['stock.move']
                res_stock_move = stock_move.read_group([('id', 'in', ids.ids)], [
                                                       'product_id', 'product_uom_qty'], ['product_id'], 0, None, False, False)
                lines = []
                for item in res_stock_move:
                    cant_prod_stock = self.compute_qty_available_prod_stock(item,item['product_id'][0])
                    if cant_prod_stock >= item['product_uom_qty']:
                        continue
                    elif (item['product_uom_qty']-cant_prod_stock) < 0:
                        continue
                    else:
                        item['product_uom_qty']-cant_prod_stock
                        lines.append((0, 0, {
                            'product_id': item['product_id'][0],
                            'ordered_qty':  math.ceil(item['product_uom_qty']-cant_prod_stock),
                        }))
                production_ids.multiple_assign()      
                
                if lines:
                    res.picking_list_summary_lines = lines
                    created_ids.append(res.id)
                else:
                    res.unlink()
                    production_ids.multiple_plan()


        return {
            'type': 'ir.actions.act_window',
            'name': 'Picking List',
            'view_mode': 'tree,form',
            'res_model': 'mrp.picking_list_summary',
            'target': 'current',
            # 'res_id': res.id,
            'domain': [('id', 'in', created_ids)],
            # 'domain': [('id', 'in', [res.id])],
        }

    @api.multi
    def button_mark_done(self):
        res = super().button_mark_done()
        self.ensure_one()
        for wo in self.workorder_ids:
            if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
                raise UserError(_('Work order %s is still running') % wo.name)
        self.post_inventory()
        moves_to_cancel = (self.move_raw_ids | self.move_finished_ids).filtered(
            lambda x: x.state not in ('done', 'cancel'))
        moves_to_cancel._action_cancel()
        self.write({'state': 'done', 'date_finished': fields.Datetime.now()})
        
        self.write({'state': 'done'})
        return self.message_post(body="Material recibido por "+self.env.user.name,
                          subtype="mail.mt_comment",
                          type="comment")


class PickingListSummary(models.Model):
    _name = 'mrp.picking_list_summary'
    _inherit = ['stock.picking', 'mail.thread', 'mail.activity.mixin']
    _description = 'Picking List Resumen'
    _rec_name = 'name'
    active = fields.Boolean(string='Archivado',default=True,required=True)
    name = fields.Char(readonly=True, copy=False,
                       default='', track_visibility='onchange')
    entrega = fields.Many2one(
        'res.users', string='Entrega', track_visibility='onchange', readonly=True)
    recibe = fields.Many2one(
        'res.users', string='Recibe', track_visibility='onchange')
    picking_list_summary_lines = fields.One2many(
        'mrp.picking_list_summary_lines', 'picking_list_summary_id', track_visibility='onchange')
    production_ids = fields.Many2many(
        'mrp.production', string="MO's", track_visibility='onchange')

    state_pkl = fields.Selection(string='Estatus', selection=[('draft', 'Lista para Procesar'), ('done', 'Materiales Entregados'), (
        'confirmed', 'Materiales Recibidos')], default='draft', help="", track_visibility='onchange')

    # routing_id = fields.Many2one('mrp.routing', string='Enrutamiento')
    configuration_id = fields.Many2one('mrp.picking_list_settings', string='Nombre de Configuracion')
    @api.model
    def create(self, values):
        # if self.search([('state_pkl','not in',['confirmed'])]):
        #     raise UserError("No se pueden crear un nuevo picking list hasta que no se reciban todos los Picking List")
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'mrp.picking_list') or _('New')
        return super(PickingListSummary, self).create(values)


    @api.multi
    def unlink(self):
        # CODE HERE
        if self.state_pkl == 'confirmed':
            raise UserError('No se puede eliminar un picking list entregado')
        for item in self:
            item.state='draft'
            for move in item.move_lines:
                move.state='draft'
        return super(PickingListSummary, self).unlink()

    @api.multi
    def validar_picking_list(self):
        configurations = self.configuration_id
        configurations.ensure_one()
        stock_picking = self.env['stock.picking']
        lines = []
        for item in self.picking_list_summary_lines:
            print(item)
            lines.append((0, 0, {
                'location_id': configurations.location_id.id,
                'location_dest_id': configurations.location_dest_id.id,
                'qty_done': item.ordered_qty,
                'product_id': item.product_id.id,
                'product_uom_id': item.product_id.uom_id.id
            }
            ))

        vals = {
            'is_locked': True,
            'location_id': configurations.location_id.id,
            'location_dest_id': configurations.location_dest_id.id,
            'move_type': configurations.move_type,
            'company_id': configurations.company_id.id,
            'picking_type_id': configurations.picking_type_id.id,
            'move_line_ids': lines}
        stock_picking = stock_picking.create(vals)

        stock_picking.button_validate()
        self.state_pkl = 'done'

    @api.multi
    def create_work_orders_pkl(self):
        self.production_ids.multiple_assign()
        self.production_ids.multiple_plan()
        self.recibe = self.env.uid
        self.state_pkl = 'confirmed'

    @api.multi
    def get_linked_mos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "MO's Asociadas",
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'target': 'current',
            # 'res_id': res.id,
            'domain': [('id', 'in',self.production_ids.ids)],
        }


class PickingListSummaryLines(models.Model):
    _name = 'mrp.picking_list_summary_lines'
    _description = 'Resumen Agrupado de Picking List'
    product_id = fields.Many2one('product.product', string='Producto')
    qty_available = fields.Float(
        compute='_compute_qty_available', string='Cantidad Disponible')
    ordered_qty = fields.Float(string='Cantidad Ordenada')

    
    @api.one
    def _compute_qty_available(self):
        # PROD/GralStock
        mrp_production = self.env['mrp.production']
        location_default = 12
        quant = mrp_production.check_availability(
            self.product_id.id, [location_default])
        self.qty_available = quant['quantity']-quant['reserved_quantity']
        return

    picking_list_summary_id = fields.Many2one('mrp.picking_list_summary')


class PickingListSettings(models.Model):
    _name = 'mrp.picking_list_settings'
    _description = 'Configuraciones de Picking List'
    _rec_name = 'name'
    name = fields.Char(string='Nombre de Configuración',
                       default="Configuración Picking List")
    location_id = fields.Many2one('stock.location', string='Origen:')
    location_dest_id = fields.Many2one('stock.location', string='Destino:')
    move_type = fields.Selection(string='Tipo de Movimiento', selection=[(
        'direct', 'Lo antes Posible'), ('One', 'Cuando todos los Productos estén Listos')])
    company_id = fields.Many2one('res.company', string='Compañia')
    picking_type_id = fields.Many2one('stock.picking.type', string='')
    rutas = fields.Many2many('mrp.routing', string='Enrutamientos')
