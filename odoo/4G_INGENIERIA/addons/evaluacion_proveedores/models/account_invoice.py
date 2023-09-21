# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'res.partner'
    pdf = fields.Binary(string="Remision:")
    pdfname = fields.Char()

    @api.one
    @api.constrains('invoice_line_ids')
    def _update_account_invoice_product_price_unit_validate(self):
        if self.origin and self.origin[:2] == 'PO':
            if self.partner_id.supplier == True:
                usuario_peritido_modificar_obj = self.env['res.users']
                usuario_peritido_modificar = usuario_peritido_modificar_obj.search(
                    [('id', '=', self._uid)])
                product_purchase_order_obj = self.env['purchase.order']
                purchase_order_origin = product_purchase_order_obj.search(
                    [('name', '=', self.origin)])
                if self.currency_id.name != purchase_order_origin.currency_id.name:
                    raise UserError(_("La moneda no coincide con la de la Orden de Compra, favor de revisar la Orden: %s " % (
                        purchase_order_origin.name)))
                for productos_factura in self.invoice_line_ids:
                    for todosloscampos_orde_compra in purchase_order_origin:
                        for productos_orden_compra in todosloscampos_orde_compra.order_line:
                            if productos_factura.product_id == productos_orden_compra.product_id:
                                maximo_autorizar = (
                                    productos_orden_compra.price_unit * 0.05) + productos_orden_compra.price_unit
                                if productos_factura.price_unit > maximo_autorizar:
                                    if usuario_peritido_modificar.x_modifica_factura_proveedor != True:
                                        raise UserError(_("El producto %s sobrepasa el monto permitido, favor de solicitar la autorizacion para modificar la factura." % (
                                            productos_factura.product_id.name)))

    def run_sql(self, origin):
        orden_compra_obj = self.env['sale.order']
        no_compra_id = orden_compra_obj.search([('name', '=', self.origin)])
        return no_compra_id.no_compra_cliente

    @api.model
    def _get_validate_account_invoice_reference_parter(self):

        self.env.cr.execute("select id, from account_invoice where reference LIKE %s and partner_id = %s; ",
                            ("%"+self.reference+"%", self.partner_id))
        validador = self.env.cr.fetchall()
        for exist_parter in validador:
            # print "FACTURA EXISTENTEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", exist_parter
            if exist_parter:
                return {'warning': {'title': "Advertencia", 'message': "La referencia de la factura %s con el proveedor %s, parece que ya se dio de alta, favor de revisar" % (self.reference, self.partner_id.name)}}

# class test_error(models.Model):
#     _name = 'test_error.test_error'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
