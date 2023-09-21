# -*- coding: utf-8 -*-

from odoo import fields, models, api,_ 
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    #aduanal = fields.Selection([('no', 'No'), ('si', 'Si')], string='Habilitar')
    #numero_pedimento = fields.Char(string=_('Numero pedimento'))

    @api.model
    def to_json(self):
        decimales = self.env['decimal.precision'].search([('name','=','Product Price')])
        no_decimales = decimales.digits
        request_params = { 
                'company': {
                      'rfc': self.company_id.rfc,
                      'api_key': self.company_id.proveedor_timbrado,
                      'modo_prueba': self.company_id.modo_prueba,
                      'regimen_fiscal': self.company_id.regimen_fiscal,
                      'postalcode': self.company_id.zip,
                      'nombre_fiscal': self.company_id.nombre_fiscal,
                      'telefono_sms': self.company_id.telefono_sms,
                },
                'customer': {
                      'name': self.partner_id.name,
                      'rfc': self.partner_id.rfc,
                      'residencia_fiscal': self.partner_id.residencia_fiscal,
                      'registro_tributario': self.partner_id.registro_tributario,
                      'uso_cfdi': self.uso_cfdi,
                },
                'invoice': {
                      'tipo_comprobante': self.tipo_comprobante,
                      'moneda': self.currency_id.name,
                      'tipocambio': self.currency_id.rate,
                      'forma_pago': self.forma_pago,
                      'methodo_pago': self.methodo_pago,
                      'subtotal': self.amount_untaxed,
                      'total': self.amount_total,
                      'folio': self.number.replace('INV','').replace('/',''),
                      'serie_factura': self.company_id.serie_factura,
                      'fecha_factura': self.fecha_factura,
                      'decimales': no_decimales,
                },
                'adicional': {
                      'tipo_relacion': self.tipo_relacion,
                      'uuid_relacionado': self.uuid_relacionado,
                      'confirmacion': self.confirmacion,
                },
        }
        amount_total = 0.0
        amount_untaxed = 0.0
        self.subtotal = 0
        self.total = 0
        self.discount = 0
        tax_grouped = {}
        items = {'numerodepartidas': len(self.invoice_line_ids)}
        invoice_lines = []
        for line in self.invoice_line_ids:
            if line.quantity < 0:
                continue
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            amounts = line.invoice_line_tax_ids.compute_all(price, line.currency_id, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            price_exclude_tax = amounts['total_excluded']
            price_include_tax = amounts['total_included']
            if line.invoice_id:
                price_exclude_tax = line.invoice_id.currency_id.round(price_exclude_tax)
                price_include_tax = line.invoice_id.currency_id.round(price_include_tax)
            amount_total += price_include_tax
            taxes = amounts['taxes']
            tax_items = []
            amount_wo_tax = line.price_unit * line.quantity
            product_taxes = {'numerodeimpuestos': len(taxes)}
            for tax in taxes:
                tax_id = self.env['account.tax'].browse(tax['id'])
                if tax_id.price_include or tax_id.amount_type == 'division':
                    amount_wo_tax -= tax['amount']
                self.monto_impuesto = tax['amount']
                tax_items.append({'name': tax_id.tax_group_id.name,
                 'percentage': tax_id.amount,
                 'amount': self.monto_impuesto, #tax['amount'],
                 'impuesto': tax_id.impuesto,
                 'tipo_factor': tax_id.tipo_factor})
                val = {'invoice_id': line.invoice_id.id,
                 'name': tax_id.tax_group_id.name,
                 'tax_id': tax['id'],
                 'amount': tax['amount']}
                key = tax['id']
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
            if tax_items:
                product_taxes.update({'tax_lines': tax_items})

            self.precio_unitario = float(amount_wo_tax) / float(line.quantity)
            self.monto = self.precio_unitario * line.quantity
            amount_untaxed += self.monto
            self.subtotal += self.monto
            self.total += self.monto + self.monto_impuesto

#            _logger.info('revisar montos ... precio unitatio %s monto %s  subtotal produto %s  subtotal acum %s', self.precio_unitario, self.monto, line.price_subtotal, self.subtotal)

            self.desc = self.monto - line.price_subtotal # p_unit * line.quantity - line.price_subtotal
            if self.desc < 0.01:
                self.desc = 0
            self.discount += self.desc

            product_string = line.product_id.code and line.product_id.code[:100] or ''
            if product_string == '':
               if line.name.find(']') > 0:
                  product_string = line.name[line.name.find('[')+len('['):line.name.find(']')] or ''

            #self.amount = p_unit * line.quantity * (1 - (line.discount or 0.0) / 100.0)
            if self.tipo_comprobante == 'E':
                invoice_lines.append({'quantity': line.quantity,
                                      'unidad_medida': line.product_id.unidad_medida,
                                      'product': product_string,
                                      'price_unit': self.precio_unitario,
                                      'amount': self.monto,
                                      'description': line.name[:1000],
                                      'clave_producto': '84111506',
                                      'clave_unidad': 'ACT',
                                      'taxes': product_taxes,
                                      'descuento': self.desc,
                                      'numero_pedimento': line.pedimento})
            elif self.tipo_comprobante == 'T':
                invoice_lines.append({'quantity': line.quantity,
                                      'unidad_medida': line.product_id.unidad_medida,
                                      'product': product_string,
                                      'price_unit': self.precio_unitario,
                                      'amount': self.monto,
                                      'description': line.name[:1000],
                                      'clave_producto': line.product_id.clave_producto,
                                      'clave_unidad': line.product_id.clave_unidad})
            else:
                invoice_lines.append({'quantity': line.quantity,
                                      'unidad_medida': line.product_id.unidad_medida,
                                      'product': product_string,
                                      'price_unit': self.precio_unitario,
                                      'amount': self.monto,
                                      'description': line.name[:1000],
                                      'clave_producto': line.product_id.clave_producto,
                                      'clave_unidad': line.product_id.clave_unidad,
                                      'taxes': product_taxes,
                                      'descuento': self.desc,
                                      'numero_pedimento': line.pedimento})

        self.discount = round(self.discount,2)
        if self.tipo_comprobante == 'T':
            request_params['invoice'].update({'subtotal': '0.00','total': '0.00'})
        else:
            request_params['invoice'].update({'subtotal': self.subtotal,'total': self.total-self.discount})
        items.update({'invoice_lines': invoice_lines})
        request_params.update({'items': items})
        tax_lines = []
        tax_count = 0
        for line in tax_grouped.values():
            tax_count += 1
            tax = self.env['account.tax'].browse(line['tax_id'])
            tax_lines.append({
                      'name': line['name'],
                      'percentage': tax.amount,
                      'amount': line['amount'],
                })
        taxes = {'numerodeimpuestos': tax_count}
        if tax_lines:
            taxes.update({'tax_lines': tax_lines})
        if not self.company_id.archivo_cer:
            raise UserError(_('Archivo .cer path is missing.'))
        if not self.company_id.archivo_key:
            raise UserError(_('Archivo .key path is missing.'))
        archivo_cer = self.company_id.archivo_cer
        archivo_key = self.company_id.archivo_key
        request_params.update({
                'certificados': {
                      'archivo_cer': archivo_cer.decode("utf-8"),
                      'archivo_key': archivo_key.decode("utf-8"),
                      'contrasena': self.company_id.contrasena,
                }})
        return request_params

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    pedimento = fields.Char('Pedimento')
