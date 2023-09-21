# -*- coding: utf-8 -*-

from odoo import api, models
import odoo.addons.decimal_precision as dp
#from odoo.exceptions import UserError

#----------------------------------------------------------
# Incoterms
#----------------------------------------------------------
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    #aduanal = fields.Selection([('no', 'No'), ('si', 'Si')], string='Habilitar')

#    @api.multi
#    def _prepare_invoice(self):
#        invoice_vals = super(SaleOrder, self)._prepare_invoice()
#        invoice_vals.update({'forma_pago': self.forma_pago,
#                    'methodo_pago': self.methodo_pago,
#                    'uso_cfdi': self.uso_cfdi,
#                    'tipo_comprobante': 'I',
#                    'aduanal': self.aduanal
#                    })
#        return invoice_vals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
        
    @api.multi
    def _prepare_invoice_line(self, qty):
        invoice_line_vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.lot_id:
            if self.lot_id.fecha_pedimento and self.lot_id.fecha_pedimento:
                if self.lot_id.lote_serie:
                    if self.product_id.tracking == 'serial':
                        invoice_line_vals.update({'name': '%s No. de serie %s %s'  % (self.name, self.lot_id.name, self.lot_id.fecha_pedimento), 'pedimento': self.lot_id.num_pedimento })
                    else:
                        invoice_line_vals.update({'name': '%s No. de lote %s %s'  % (self.name, self.lot_id.name, self.lot_id.fecha_pedimento), 'pedimento': self.lot_id.num_pedimento })
                else:
                    invoice_line_vals.update({'name': '%s %s'  % (self.name, self.lot_id.fecha_pedimento), 'pedimento': self.lot_id.num_pedimento})
            else:
                if self.product_id.tracking == 'serial':
                    invoice_line_vals.update({'name': '%s No. de serie %s'  % (self.name, self.lot_id.name)})
                else:
                    invoice_line_vals.update({'name': '%s No. de lote %s'  % (self.name, self.lot_id.name)})
                #raise UserError(_('Falta fecha o número de pediemnto en el lote.'))
        return invoice_line_vals
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
