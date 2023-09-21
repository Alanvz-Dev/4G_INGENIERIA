from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import date, datetime, time, timedelta


class purchase_order(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    apoyo = fields.Boolean('Costo especial')
    categoria_costo = fields.Many2one('categorycost.product', 'Nombre del producto')
    cost_category = fields.Float('Costo temporal', digits=(14, 2))
    cuenta_analitica = fields.Many2one('account.analytic.account', 'Cuenta Analitica / Proyecto', no_create=True)
    autorizacion_compras = fields.Boolean('Liberada por Compras')
    pendiente_envio = fields.Boolean('Pendiente Envio OC', readonly=True)

    @api.one
    def button_approve(self):
        res = super(purchase_order, self).button_approve()
        self.write({'pendiente_envio': True})
        return res

    @api.one
    def button_cancel(self):
        res = super(purchase_order, self).button_cancel()
        self.write({'pendiente_envio': False})
        return res

    @api.multi
    def button_send_po(self):
        self.write({'pendiente_envio': False})
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference(
                    'purchase', 'email_template_edi_purchase_done')[1]
            else:
                template_id = ir_model_data.get_object_reference(
                    'purchase', 'email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    # @api.onchange('categoria_costo')
    # def onchange_precio_categoria(self):
    #     self.cost_category = self.categoria_costo.cost

    @api.multi  # (cr, uid, ids, context)
    def update_price_order_list(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        product = self.env['product.template']
        res = 0.0
        for var in self.order_line:
            real_supplierinfo_id = supplierinfo_obj.search(
                [('product_tmpl_id', '=', var.product_id.id)])
            real_category_id = product.search(
                [('category_product_id', '=', self.categoria_costo.id)])
            for var2 in real_supplierinfo_id:
                res = var2.real_price*self.cost_category
                for igualacion in real_category_id:
                    if var.product_id.id == igualacion.id:
                        var.write({'price_unit': res})
        lineas = self.order_line.search([('product_id', '=', self.id)])

    @api.multi  # (cr, uid, ids, context)
    def update_cuanta_analitica(self):
        # print "############ cuenta seleccionada >>>>>>>>> ", self.cuenta_analitica.id
        if self.cuenta_analitica.id:
            for lines in self.order_line:
                lines.write({'account_analytic_id': self.cuenta_analitica.id})
        else:
            raise UserError(
                _("No se a seleccionado cuenta analitica o proyecto"))

    @api.one  # (cr, uid, ids, context)
    def button_confirm(self):
        res = super(purchase_order, self).button_confirm()
        if self.partner_id.partner_invalid != False:
            raise UserError(
                _("No se puede asignar este proveedor para una Orden de Compra."))
        return res
