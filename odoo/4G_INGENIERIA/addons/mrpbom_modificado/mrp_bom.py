# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.addons import decimal_precision as dp


class AsistenteMaterialRequired(models.Model):
    _name = 'asistente.material.required'
    _inherit='mrp.bom'


    @api.model  
    def default_get(self, fields):
        res = super(AsistenteMaterialRequired, self).default_get(fields)
        record_ids = self._context.get('active_ids', [])
        mrp_obj = self.env['mrp.production']
        if not record_ids:
            return {}
        material_list = []
        quotation_request_create = False
        supplier_id = False
        #lines_wo_supplier = False
        for mrp in mrp_obj.browse(record_ids):
            quotation_request_create = mrp.quotation_request_create
            for product in mrp.move_raw_ids:
                #if not product.product_id.seller_ids:
                    #lines_wo_supplier = True
                qty_need = product.product_uom_qty
                qty_reservated = product.product_id.qty_available_not_res
                
                mrp_uom = product.product_uom
                product_uom = product.product_id.uom_id
                if mrp_uom != product_uom:
                    uom = product_uom
                    qty_reservated = uom._compute_quantity(qty_reservated, mrp_uom)

                qty_to_purchase = 0.0
                if qty_reservated < qty_need:
                    qty_to_purchase = qty_need - qty_reservated

                material_list.append((0,0,{
                    'product_id': product.product_id.id,
                    'uom_id': product.product_uom.id,
                    'qty_need': qty_need,
                    'qty_reservated': qty_reservated,
                    'qty_to_purchase': qty_to_purchase,
                    'product_wo_supplier': True if not product.product_id.seller_ids else False,
                    'product_wo_supplier_id': product.product_id.seller_ids[0].id if product.product_id.seller_ids else False,
                        }))
        res.update(material_ids=material_list, quotation_request_create=quotation_request_create)
        return res


    material_ids = fields.One2many( 'asistente.material.required.line', 'wizard_id', 'Detalle Materiales')
    date_purchase = fields.Datetime('Fecha Planificada', default=fields.Datetime.now)
    quotation_request_create = fields.Boolean('Solicitud Creada')
    supplier_id = fields.Many2one('res.partner', 'Proveedor Comodin')
    quotation_exception_supplier = fields.Boolean('Crear Presupuesto para Excepciones')
    lines_wo_supplier = fields.Boolean('Productos sin Proveedor')
    #product_wo_supplier_id = fields.Many2one('product.supplierinfo','Proveedor del producto')


    @api.multi
    def make_orders(self):
        active_ids = self._context['active_ids']
        purchase_order = self.env['purchase.order']
        purchase_line_order = self.env['purchase.order.line']
        mrp_obj = self.env['mrp.production']
        vals = {}
        order_id = False
        purchase_list = []
        for rec in self:
            mrp_browse = mrp_obj.browse(active_ids)
            mrp_browse.write({'quotation_request_create':True})
            order_line = []
            taxes_id = False
            partner_purchase_list = {}
            purchase_exception_line = []
            for line in rec.material_ids:
                if line.qty_to_purchase > 0.0:
                    if line.product_id.supplier_taxes_id:
                        taxes_id = [x.id for x in line.product_id.supplier_taxes_id]
                    try:
                        name_get = line.product_id.name_get()[0]
                        name_complete = '[ '+name_get[0]+' ] '+name_get[1]
                    except:
                        name_complete = line.product_id.name
                    xline = (0,0,{
                            'product_id': line.product_id.id,
                            'name': name_complete,
                            'account_analytic_id': mrp_browse[0].analytic_account_id.id if mrp_browse[0].analytic_account_id else False,
                            'product_qty': line.qty_to_purchase,
                            'product_uom': line.uom_id.id,
                            'taxes_id': [(6,0,taxes_id)] if taxes_id else False,
                            #'taxes_id': line.product_wo_supplier_id,
                            'price_unit': 0.0,
                            'date_planned': rec.date_purchase,
                        })
                    supplier_id = line.product_wo_supplier_id.name

                    if supplier_id not in partner_purchase_list:
                        partner_purchase_list.update({supplier_id:[]})

                    partner_purchase_list[supplier_id].append(xline)
            quotation_name_list = []
            for toorder in partner_purchase_list:
                order_line = partner_purchase_list[toorder]
                purchase_prev = purchase_order.search([('from_mrp_order','=',True),('state','=','draft'),('partner_id','=',toorder.id)])
                if order_line:
                    if not purchase_prev:
                        vals = {
                            'partner_id': toorder.id,
                            'date_order': rec.date_purchase,                            
                            'order_line': order_line,
                            'origin': mrp_browse[0].name,
                            'from_mrp_order': True,
                        }
                        order_id = purchase_order.create(vals)
                        for line in order_id.order_line:
                            line._onchange_quantity()
                        purchase_list.append(order_id.id)
                        quotation_name_list.append(str(order_id.name))
                    else:
                        purchase_prev = purchase_prev[0]
                        for poline in order_line:
                            order_line_val  = poline[2]
                            order_line_val['order_id'] = purchase_prev.id
                            purchase_line_extend = False
                            for line in purchase_prev.order_line:
                                if line.product_id.id == poline[2]['product_id'] and line.account_analytic_id.id == poline[2]['account_analytic_id']:
                                    line.product_qty = line.product_qty + poline[2]['product_qty']
                                    purchase_line_extend = True
                            if purchase_line_extend == False:
                                purchase_line_order.create(poline[2])

                            if purchase_prev.id not in purchase_list:
                                purchase_list.append(purchase_prev.id)
                            if str(purchase_prev.name) not in quotation_name_list:
                                quotation_name_list.append(str(purchase_prev.name))
                            for line in purchase_prev.order_line:
                                line._onchange_quantity()
                        if mrp_browse[0].name not in purchase_prev.origin:
                            purchase_prev.write({
                                        'origin': purchase_prev.origin+", "+mrp_browse[0].name
                                })

            if purchase_exception_line:
                partner_purchase_ids_list = [x.id for x in partner_purchase_list]
                purchase_prev = purchase_order.search([('from_mrp_order','=',True),('state','=','draft'),('partner_id','not in',tuple(partner_purchase_ids_list))])
                if rec.quotation_exception_supplier:
                    if order_line:
                        if not purchase_prev:
                            vals = {
                                'partner_id': rec.supplier_id.id,
                                'date_order': rec.date_purchase,
                                'order_line': purchase_exception_line,
                                'origin': mrp_browse[0].name,
                                'from_mrp_order': True,
                            }
                            order_id = purchase_order.create(vals)
                            for line in order_id.order_line:
                                line._onchange_quantity()
                            purchase_list.append(order_id.id)
                            quotation_name_list.append(str(order_id.name))
                        else:
                            purchase_prev = purchase_prev[0]
                            for poline in purchase_exception_line:
                                order_line_val  = poline[2]
                                order_line_val['order_id'] = purchase_prev.id
                                purchase_line_extend = False
                                for line in purchase_prev.order_line:
                                    if line.product_id.id == poline[2]['product_id'] and line.account_analytic_id.id == poline[2]['account_analytic_id']:
                                        line.product_qty = line.product_qty + poline[2]['product_qty']
                                        purchase_line_extend = True
                                if purchase_line_extend == False:
                                    purchase_line_order.create(poline[2])
                                if purchase_prev.id not in purchase_list:
                                    purchase_list.append(purchase_prev.id)

                                if str(purchase_prev.name) not in quotation_name_list:
                                    quotation_name_list.append(str(purchase_prev.name))
                                for line in purchase_prev.order_line:
                                    line._onchange_quantity()
                            if mrp_browse[0].name not in purchase_prev.origin:
                                purchase_prev.write({
                                        'origin': purchase_prev.origin+", "+mrp_browse[0].name
                                })
                                
            mrp_browse.write({'quotation_name_list': str(quotation_name_list).replace(",","")})

        return {
                    'domain': [('id', 'in', purchase_list)],
                    'name': _('Compras de Produccion'),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'context': {'tree_view_ref': 'purchase.purchase_order_tree'},
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window'
                    }