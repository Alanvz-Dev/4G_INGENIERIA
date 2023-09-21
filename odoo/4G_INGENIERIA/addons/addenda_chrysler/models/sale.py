# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class  EnvioChrysler(models.Model):
    _name = 'addenda.chrysler.envio'
    _rec_name = 'envio_nombre'

    envio_codigo = fields.Char("Código")
    envio_nombre = fields.Char("Nombre de la Planta / Almacén")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    codigo_envio = fields.Many2one('addenda.chrysler.envio', string='Dirección de envío')
    orden_compra = fields.Char(string='Orden de compra')
    requicision_liberacion = fields.Char(string='Requisición de liberación')
    chrysler_addenda = fields.Boolean(string='Addenda Chrysler', default=False)
    fca_tipodocumento = fields.Selection(
        selection=[('PUA', 'PUA'), 
                   ('PPY', 'PPY'),],
        string=_('Tipo de documento'),
    )

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'chrysler_addenda': self.chrysler_addenda,
                             'orden_compra': self.orden_compra,
                             'requicision_liberacion': self.requicision_liberacion,
                             'codigo_envio': self.codigo_envio.id,
                             'fca_tipodocumento': self.fca_tipodocumento,
                    })
        return invoice_vals
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    no_parte = fields.Char(string="No. parte.")
    line_item = fields.Char(string="Line item")
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    no_parte = fields.Char(string="No. parte.")
    line_item = fields.Char(string="Line item")
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        res =super(SaleOrderLine,self)._prepare_invoice_line(qty)
        vals={
            'no_parte':self.no_parte,
            'line_item':self.line_item
            }
        res.update(vals)
        return res