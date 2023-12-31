# -*- coding: utf-8 -*-

import base64
import json
import requests
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from . import amount_to_text_es_MX
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import mm
from datetime import datetime, timedelta
import pytz
from .tzlocal import get_localzone
from odoo import tools
import math

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    forma_pago = fields.Selection(selection=[('01', '01 - Efectivo'), 
                   ('02', '02 - Cheque nominativo'), 
                   ('03', '03 - Transferencia electrónica de fondos'),
                   ('04', '04 - Tarjeta de Crédito'), 
                   ('05', '05 - Monedero electrónico'),
                   ('06', '06 - Dinero electrónico'), 
                   ('08', '08 - Vales de despensa'), 
                   ('12', '12 - Dación en pago'), 
                   ('13', '13 - Pago por subrogación'), 
                   ('14', '14 - Pago por consignación'), 
                   ('15', '15 - Condonación'), 
                   ('17', '17 - Compensación'), 
                   ('23', '23 - Novación'), 
                   ('24', '24 - Confusión'), 
                   ('25', '25 - Remisión de deuda'), 
                   ('26', '26 - Prescripción o caducidad'), 
                   ('27', '27 - A satisfacción del acreedor'), 
                   ('28', '28 - Tarjeta de débito'), 
                   ('29', '29 - Tarjeta de servicios'), 
                   ('30', '30 - Aplicación de anticipos'),
                   ('31', '31 - Intermediario pagos'), ],
                                string=_('Forma de pago'), 
                            )
    tipo_comprobante = fields.Selection(
                                selection=[ ('P', 'Pago'),],
                                string=_('Tipo de comprobante'), default='P',
                            )
    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
                   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), 
    )
#    no_de_pago = fields.Integer("No. de pago", readonly=True)
    #saldo_pendiente = fields.Float("Saldo pendiente", readonly=True)
    #monto_pagar = fields.Float("Monto a pagar", compute='_compute_monto_pagar')
    #saldo_restante = fields.Float("Saldo restante", readonly=True)
    fecha_pago = fields.Datetime("Fecha de pago")
    cuenta_emisor = fields.Many2one('res.partner.bank', string=_('Cuenta del emisor'))
    banco_emisor = fields.Char("Banco del emisor", related='cuenta_emisor.bank_name', readonly=True)
    rfc_banco_emisor = fields.Char(_("RFC banco emisor"), related='cuenta_emisor.bank_bic', readonly=True)
    numero_operacion = fields.Char(_("Número de operación"))
    banco_receptor = fields.Char(_("Banco receptor"), compute='_compute_banco_receptor')
    cuenta_beneficiario = fields.Char(_("Cuenta beneficiario"), compute='_compute_banco_receptor')
    rfc_banco_receptor = fields.Char(_("RFC banco receptor"), compute='_compute_banco_receptor')
    estado_pago = fields.Selection(
        selection=[('pago_no_enviado', 'REP no generado'), ('pago_correcto', 'REP correcto'), 
                   ('problemas_factura', 'Problemas con el pago'), ('solicitud_cancelar', 'Cancelación en proceso'),
                   ('cancelar_rechazo', 'Cancelación rechazada'), ('factura_cancelada', 'REP cancelado'), ],
        string=_('Estado CFDI'),
        default='pago_no_enviado',
        readonly=True
    )
    tipo_relacion = fields.Selection(
        selection=[('04', 'Sustitución de los CFDI previos'),],
        string=_('Tipo relación'),
    )
    uuid_relacionado = fields.Char(string=_('CFDI Relacionado'))
    confirmacion = fields.Char(string=_('Confirmación'))
    folio_fiscal = fields.Char(string=_('Folio Fiscal'), readonly=True)
    numero_cetificado = fields.Char(string=_('Numero de certificado'))
    cetificaso_sat = fields.Char(string=_('Cetificado SAT'))
    fecha_certificacion = fields.Char(string=_('Fecha y Hora Certificación'))
    cadena_origenal = fields.Char(string=_('Cadena Original del Complemento digital de SAT'))
    selo_digital_cdfi = fields.Char(string=_('Sello Digital del CDFI'))
    selo_sat = fields.Char(string=_('Sello del SAT'))
 #   moneda = fields.Char(string=_('Moneda'))
    monedap = fields.Char(string=_('Moneda'))
#    tipocambio = fields.Char(string=_('TipoCambio'))
    tipocambiop = fields.Char(string=_('TipoCambio'))
    folio = fields.Char(string=_('Folio'))
  #  version = fields.Char(string=_('Version'))
    number_folio = fields.Char(string=_('Folio'), compute='_get_number_folio')
    amount_to_text = fields.Char('Amount to Text', compute='_get_amount_to_text',
                                 size=256, 
                                 help='Amount of the invoice in letter')
    qr_value = fields.Char(string=_('QR Code Value'))
    qrcode_image = fields.Binary("QRCode")
#    rfc_emisor = fields.Char(string=_('RFC'))
#    name_emisor = fields.Char(string=_('Name'))
    xml_payment_link = fields.Char(string=_('XML link'), readonly=True)
    payment_mail_ids = fields.One2many('account.payment.mail', 'payment_id', string='Payment Mails')
    iddocumento = fields.Char(string=_('iddocumento'))
    fecha_emision = fields.Char(string=_('Fecha y Hora Certificación'))
    docto_relacionados = fields.Text("Docto relacionados",default='[]')
    cep_sello = fields.Char(string=_('cep_sello'))
    cep_numeroCertificado = fields.Char(string=_('cep_numeroCertificado'))
    cep_cadenaCDA = fields.Char(string=_('cep_cadenaCDA'))
    cep_claveSPEI = fields.Char(string=_('cep_claveSPEI'))
    retencionesp = fields.Text("traslados P",default='[]')
    trasladosp = fields.Text("retenciones P",default='[]')
    total_pago = fields.Float("Total pagado") 

    @api.depends('name')
    def _get_number_folio(self):
        for record in self:
            if record.number:
                record.number_folio = record.name.replace('CUST.IN','').replace('/','')

    @api.model
    def get_docto_relacionados(self,payment):
        try:
            data = json.loads(payment.docto_relacionados)
        except Exception:
            data = []
        return data
    
    @api.multi
    def importar_incluir_cep(self):
        ctx = {'default_payment_id':self.id}
        return {
            'name': _('Importar factura de compra'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('cdfi_invoice.view_import_xml_payment_in_payment_form_view').id,
            'res_model': 'import.account.payment.from.xml',
            'context': ctx,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        
    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            self.forma_pago = self.journal_id.forma_pago
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}
    
    @api.onchange('payment_date')
    def _onchange_payment_date(self):
        if self.payment_date:
            self.fecha_pago = self.payment_date+' 12:00:00'

    @api.multi
    def add_resitual_amounts(self):
        for payment in self:
          no_decimales = payment.currency_id.no_decimales
          no_decimales_tc = payment.currency_id.no_decimales_tc
          docto_relacionados = []
          tax_grouped_tras = {}
          tax_grouped_ret = {}
          mxn_currency = self.env["res.currency"].search([('name', '=', 'MXN')], limit=1)

          if payment.invoice_ids:
            invoice_vals_list = []
            pay_rec_lines = payment.move_line_ids.filtered(lambda line: line.account_id.internal_type in ('receivable', 'payable'))

            if payment.currency_id == mxn_currency:
               rate_payment_curr_mxn = None
               paid_amount_comp_curr = payment.amount
            else:
               rate_payment_curr_mxn = payment.currency_id.with_context(date=self.payment_date).rate 
               paid_amount_comp_curr = payment.currency_id.round(payment.amount * rate_payment_curr_mxn)

            for partial in pay_rec_lines['matched_debit_ids']:
                   payment_line = partial['credit_move_id']
                   invoice_line = partial['debit_move_id']
                   invoice_amount = partial['amount']
                   invoice = invoice_line.invoice_id
                   decimal_p = 6

                   if partial.amount == 0:
                       raise Warning("Una factura adjunta en el pago no tiene un monto liquidado por el pago. \nRevisa que todas las facturas tengan un monto pagado, puede ser necesario desvincular las facturas y vinculalas en otro orden.")

                   if invoice.currency_id != mxn_currency:
                        invoice_amount = invoice_amount * partial.amount_currency / partial.amount

                   if not invoice.factura_cfdi:
                       continue

                   payment_dict = json.loads(invoice.payments_widget)
                   payment_content = payment_dict['content']

                   if invoice.total_factura <= 0:
                       raise Warning("No hay monto total de la factura. Carga el XML en la factura para agregar el monto total.")

                   if invoice.currency_id == payment.currency_id:
                       amount_paid_invoice_curr = invoice_amount
                       equivalenciadr = 1
                   elif invoice.currency_id == mxn_currency and invoice.currency_id != payment.currency_id:
                       amount_paid_invoice_curr = invoice_amount
                       paid_amount_comp_curr = payment.amount  * 1 / rate_payment_curr_mxn
                       amount_paid_invoice_comp_curr = payment.company_id.currency_id.round(payment.amount  * (abs(payment_line.balance) / paid_amount_comp_curr))
                       invoice_rate = partial.amount_currency / partial.amount
                       exchange_rate = amount_paid_invoice_curr / amount_paid_invoice_comp_curr
                       equivalenciadr = payment.roundTraditional(exchange_rate, decimal_p) + 0.000001
                   else:
                       amount_paid_invoice_curr = invoice_amount
                       exchange_rate = partial.amount_currency / partial.amount
                       equivalenciadr = payment.roundTraditional(exchange_rate, decimal_p) + 0.000001
                   paid_pct = payment.truncate(amount_paid_invoice_curr, decimal_p) / invoice.total_factura

                   if not invoice.tax_payment:
                       raise Warning("No hay información de impuestos en el documento. Carga el XML en la factura para agregar los impuestos.")
                   taxes = json.loads(invoice.tax_payment)
                   objetoimpdr = '01'
                   trasladodr = []
                   retenciondr = []
                   if "translados" in taxes:
                       objetoimpdr = '02'
                       traslados = taxes['translados']
                       for traslado in traslados:
                           basedr = payment.truncate(float(traslado['base']) * paid_pct, decimal_p)
                           importedr = traslado['importe'] and payment.truncate(float(traslado['tasa']) * basedr, decimal_p) or 0
                           trasladodr.append({
                                         'BaseDR': payment.set_decimals(basedr, decimal_p),
                                         'ImpuestoDR': traslado['impuesto'],
                                         'TipoFactorDR': traslado['TipoFactor'],
                                         'TasaOcuotaDR': traslado['tasa'],
                                         'ImporteDR': payment.set_decimals(importedr, decimal_p) if traslado['TipoFactor'] != 'Exento' else '',
                                         })
                           key = traslado['tax_id']

                           basep = basedr / equivalenciadr
                           importep = importedr / equivalenciadr
                           if str(basep)[::-1].find('.') > 6:
                              basep = payment.truncate(basep, decimal_p)
                           if str(importep)[::-1].find('.') > 6:
                              importep = payment.truncate(importep, decimal_p)

                           val = {'BaseP': basep,
                                  'ImpuestoP': traslado['impuesto'],
                                  'TipoFactorP': traslado['TipoFactor'],
                                  'TasaOCuotaP': traslado['tasa'],
                                  'ImporteP': importep,}
                           if key not in tax_grouped_tras:
                               tax_grouped_tras[key] = val
                           else:
                               tax_grouped_tras[key]['BaseP'] += basep
                               tax_grouped_tras[key]['ImporteP'] += importep
                   if "retenciones" in taxes:
                       objetoimpdr = '02'
                       retenciones = taxes['retenciones']
                       for retencion in retenciones:
                           basedr = payment.truncate(float(retencion['base']) * paid_pct, decimal_p)
                           importedr = retencion['importe'] and payment.truncate(float(retencion['tasa']) * basedr, decimal_p) or 0
                           retenciondr.append({
                                         'BaseDR': payment.set_decimals(basedr, decimal_p),
                                         'ImpuestoDR': retencion['impuesto'],
                                         'TipoFactorDR': retencion['TipoFactor'],
                                         'TasaOcuotaDR': retencion['tasa'],
                                         'ImporteDR': payment.set_decimals(importedr, decimal_p),
                                         })
                           key = retencion['tax_id']

                           importep = importedr / equivalenciadr
                           if str(importep)[::-1].find('.') > 6:
                              importep = payment.truncate(importep, decimal_p)

                           val = {'ImpuestoP': retencion['impuesto'],
                                  'ImporteP': importep,}
                           if key not in tax_grouped_ret:
                               tax_grouped_ret[key] = val
                           else:
                               tax_grouped_ret[key]['ImporteP'] += importep

                   docto_relacionados.append({
                          'MonedaDR': invoice.moneda,
                          'EquivalenciaDR': equivalenciadr,
                          'IdDocumento': invoice.folio_fiscal,
                          'folio_facura': invoice.number_folio,
                          'NumParcialidad': len(payment_content),
                          'ImpSaldoAnt': payment.roundTraditional(min(invoice.residual + amount_paid_invoice_curr, invoice.amount_total), no_decimales),
                          'ImpPagado': payment.roundTraditional(amount_paid_invoice_curr, no_decimales),
                          'ImpSaldoInsoluto': payment.roundTraditional(min(invoice.residual + amount_paid_invoice_curr, invoice.amount_total), no_decimales) - \
                                              payment.roundTraditional(amount_paid_invoice_curr, no_decimales),
                          'ObjetoImpDR': objetoimpdr,
                          'ImpuestosDR': {'traslados': trasladodr, 'retenciones': retenciondr,},
                   })

            payment.write({'docto_relacionados': json.dumps(docto_relacionados), 
                        'retencionesp': json.dumps(tax_grouped_ret), 
                        'trasladosp': json.dumps(tax_grouped_tras),})

    def post(self):
        res = super(AccountPayment, self).post()
        for rec in self:
    #        rec.add_resitual_amounts()
            rec._onchange_payment_date()
            rec._onchange_journal()
        return res

    @api.one
    @api.depends('amount')
    def _compute_monto_pagar(self):
        for record in self:
            if record.amount:
                record.monto_pagar = record.amount
            else:
                record.monto_pagar = 0

    @api.one
    @api.depends('journal_id')
    def _compute_banco_receptor(self):
        for record in self:
           if record.journal_id and record.journal_id.bank_id:
               record.banco_receptor = record.journal_id.bank_id.name
               record.rfc_banco_receptor = record.journal_id.bank_id.bic
           if record.journal_id:
               record.cuenta_beneficiario = record.journal_id.bank_acc_number

    @api.one
    @api.depends('amount', 'currency_id')
    def _get_amount_to_text(self):
        for record in self:
            record.amount_to_text = amount_to_text_es_MX.get_amount_to_text(record, record.amount_total, 'es_cheque', record.currency_id.name)
        
    @api.model
    def _get_amount_2_text(self, amount_total):
        return amount_to_text_es_MX.get_amount_to_text(self, amount_total, 'es_cheque', self.currency_id.name)
            
    @api.model
    def to_json(self):
        if self.partner_id.rfc == 'XAXX010101000' or self.partner_id.rfc == 'XEXX010101000':
            zipreceptor = self.journal_id.codigo_postal or self.company_id.zip
        else:
            zipreceptor = self.partner_id.zip

        no_decimales = self.currency_id.no_decimales
        no_decimales_tc = self.currency_id.no_decimales_tc

        self.monedap = self.currency_id.name
        if self.currency_id.name == 'MXN':
            self.tipocambiop = '1'
        else:
            self.tipocambiop = self.set_decimals(1 / self.currency_id.with_context(date=self.payment_date).rate, no_decimales_tc)

        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.env.user.partner_id.tz or 'America/Mexico_City'
        #timezone = tools.ustr(timezone).encode('utf-8')

        if not self.fecha_pago:
            raise Warning("Falta configurar fecha de pago en la sección de CFDI del documento.")
        else:
            local = pytz.timezone(timezone)
            naive_from = datetime.strptime(self.fecha_pago, '%Y-%m-%d %H:%M:%S')
            local_dt_from = naive_from.replace(tzinfo=pytz.UTC).astimezone(local)
            date_from = local_dt_from.strftime ("%Y-%m-%dT%H:%M:%S")
        self.add_resitual_amounts()

        #corregir hora
        local2 = pytz.timezone(timezone)
        naive_from2 = datetime.now() 
        local_dt_from2 = naive_from2.replace(tzinfo=pytz.UTC).astimezone(local2)
        date_payment = local_dt_from2.strftime ("%Y-%m-%dT%H:%M:%S")

        self.check_cfdi_values()

        conceptos = []
        conceptos.append({
                          'ClaveProdServ': '84111506',
                          'ClaveUnidad': 'ACT',
                          'cantidad': 1,
                          'descripcion': 'Pago',
                          'valorunitario': '0',
                          'importe': '0',
                          'ObjetoImp': '01',
                    })

        taxes_traslado = json.loads(self.trasladosp)
        taxes_retenciones = json.loads(self.retencionesp)
        impuestosp = {}
        totales = {}
        self.total_pago = 0
        if taxes_traslado or taxes_retenciones:
           retencionp = []
           trasladop = []
           if taxes_traslado:
              for line in taxes_traslado.values():
                  trasladop.append({'ImpuestoP': line['ImpuestoP'],
                                    'TipoFactorP': line['TipoFactorP'],
                                    'TasaOCuotaP': line['TasaOCuotaP'],
                                    'ImporteP': self.set_decimals(line['ImporteP'],6) if line['TipoFactorP'] != 'Exento' else '',
                                    'BaseP': self.set_decimals(line['BaseP'],6),
                                    })
                  if line['ImpuestoP'] == '002' and line['TasaOCuotaP'] == '0.160000':
                       totales.update({'TotalTrasladosBaseIVA16': self.roundTraditional(line['BaseP'] * float(self.tipocambiop),2),
                                       'TotalTrasladosImpuestoIVA16': self.roundTraditional(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '002' and line['TasaOCuotaP'] == '0.080000':
                       totales.update({'TotalTrasladosBaseIVA8': self.roundTraditional(line['BaseP'] * float(self.tipocambiop),2),
                                       'TotalTrasladosImpuestoIVA8': self.roundTraditional(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '002' and line['TasaOCuotaP'] == '0.000000':
                       totales.update({'TotalTrasladosBaseIVA0': self.roundTraditional(line['BaseP'] * float(self.tipocambiop),2),
                                       'TotalTrasladosImpuestoIVA0': self.roundTraditional(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '002' and line['TipoFactorP'] == 'Exento':
                       totales.update({'TotalTrasladosBaseIVAExento': self.roundTraditional(line['BaseP'] * float(self.tipocambiop),2),})
                  if line['TipoFactorP'] != 'Exento':
                     self.total_pago += round(line['BaseP'] * float(self.tipocambiop),2) + round(line['ImporteP'] * float(self.tipocambiop),2)
                  else:
                     self.total_pago += round(line['BaseP'] * float(self.tipocambiop),2)
              impuestosp.update({'TrasladosP': trasladop})
           if taxes_retenciones:
              for line in taxes_retenciones.values():
                  retencionp.append({'ImpuestoP': line['ImpuestoP'],
                                    'ImporteP': self.set_decimals(line['ImporteP'],6),
                                    })
                  if line['ImpuestoP'] == '002':
                       totales.update({'TotalRetencionesIVA': self.roundTraditional(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '001':
                       totales.update({'TotalRetencionesISR': self.roundTraditional(line['ImporteP'] * float(self.tipocambiop),2),})
                  if line['ImpuestoP'] == '003':
                       totales.update({'TotalRetencionesIEPS': self.roundTraditional(line['ImporteP']* float(self.tipocambiop),2),})
                  self.total_pago -= round(line['ImporteP'] * float(self.tipocambiop),2)
              impuestosp.update({'RetencionesP': retencionp})
        totales.update({'MontoTotalPagos': self.set_decimals(self.amount, 2) if self.monedap == 'MXN' else self.set_decimals(self.amount * float(self.tipocambiop), 2),})
        #totales.update({'MontoTotalPagos': self.set_decimals(self.total_pago, 2),})

        pagos = []
        pagos.append({
                      'FechaPago': date_from,
                      'FormaDePagoP': self.forma_pago,
                      'MonedaP': self.monedap,
                      'TipoCambioP': self.tipocambiop, # if self.monedap != 'MXN' else '1',
                      'Monto':  self.set_decimals(self.amount, no_decimales),
                      #'Monto':  self.set_decimals(self.total_pago/float(self.tipocambiop), no_decimales),
                      'NumOperacion': self.numero_operacion,

                      'RfcEmisorCtaOrd': self.rfc_banco_emisor if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'NomBancoOrdExt': self.banco_emisor if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'CtaOrdenante': self.cuenta_emisor.acc_number if self.cuenta_emisor and self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'RfcEmisorCtaBen': self.rfc_banco_receptor if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'CtaBeneficiario': self.cuenta_beneficiario if self.forma_pago in ['02', '03', '04', '05', '28', '29'] else '',
                      'DoctoRelacionado': json.loads(self.docto_relacionados),
                      'ImpuestosP': impuestosp,
                    })

        if self.invoice_ids:
            request_params = {
                'factura': {
                      'serie': self.journal_id.serie_diario or self.company_id.serie_complemento,
                      'folio': self.name.replace('CUST.IN','').replace('/',''),
                      'fecha_expedicion': date_payment,
                      'subtotal': '0',
                      'moneda': 'XXX',
                      'total': '0',
                      'tipocomprobante': 'P',
                      'LugarExpedicion': self.journal_id.codigo_postal or self.company_id.zip,
                      'confirmacion': self.confirmacion,
                      'Exportacion': '01',
                },
                'emisor': {
                      'rfc': self.company_id.rfc.upper(),
                      'nombre': self.company_id.nombre_fiscal.upper(),
                      'RegimenFiscal': self.company_id.regimen_fiscal,
                },
                'receptor': {
                      'nombre': self.partner_id.name.upper(),
                      'rfc': self.partner_id.rfc.upper(),
                      'ResidenciaFiscal': self.partner_id.residencia_fiscal,
                      'NumRegIdTrib': self.partner_id.registro_tributario,
                      'UsoCFDI': 'CP01',
                      'RegimenFiscalReceptor': self.partner_id.regimen_fiscal,
                      'DomicilioFiscalReceptor': zipreceptor,
                },

                'informacion': {
                      'cfdi': '4.0',
                      'sistema': 'odoo11',
                      'version': '6',
                      'api_key': self.company_id.proveedor_timbrado,
                      'modo_prueba': self.company_id.modo_prueba,
                },

                'conceptos': conceptos,

                'totales': totales,

                'pagos20': {'Pagos': pagos},

            }

            if self.uuid_relacionado:
              cfdi_relacionado = []
              uuids = self.uuid_relacionado.replace(' ','').split(',')
              for uuid in uuids:
                   cfdi_relacionado.append({
                         'uuid': uuid,
                   })
              request_params.update({'CfdisRelacionados': {'UUID': cfdi_relacionado, 'TipoRelacion':self.tipo_relacion }})

        else:
            raise Warning("No tiene ninguna factura ligada al documento de pago, debe al menos tener una factura ligada. \n Desde la factura crea el pago para que se asocie la factura al pago.")
        return request_params

    def check_cfdi_values(self):
        if not self.company_id.rfc:
            raise UserError(_('El emisor no tiene RFC configurado.'))
        if not self.company_id.name:
            raise UserError(_('El emisor no tiene nombre configurado.'))
        if not self.partner_id.rfc:
            raise UserError(_('El receptor no tiene RFC configurado.'))
        if not self.company_id.regimen_fiscal:
            raise UserError(_('El emisor no régimen fiscal configurado.'))
        if not self.journal_id.codigo_postal and not self.company_id.zip:
            raise UserError(_('El emisor no tiene código postal configurado.'))
        if not self.forma_pago:
            raise UserError(_('Falta configurar la forma de pago.'))

    def set_decimals(self, amount, precision):
        if amount is None or amount is False:
            return None
        return '%.*f' % (precision, amount)

    def roundTraditional(self, val, digits):
       if val != 0:
          return round(val + 10 ** (-len(str(val)) - 1), digits)
       else:
          return 0

    def clean_text(self, text):
        clean_text = text.replace('\n', ' ').replace('\\', ' ').replace('-', ' ').replace('/', ' ').replace('|', ' ')
        clean_text = clean_text.replace(',', ' ').replace(';', ' ').replace('>', ' ').replace('<', ' ')
        return clean_text[:1000]

    @api.multi
    def complete_payment(self):
        for p in self:
            if p.folio_fiscal:
                 p.write({'estado_pago': 'pago_correcto'})
                 return True

            values = p.to_json()
            if self.company_id.proveedor_timbrado == 'multifactura':
                url = '%s' % ('http://facturacion.itadmin.com.mx/api/payment')
            elif self.company_id.proveedor_timbrado == 'multifactura2':
                url = '%s' % ('http://facturacion2.itadmin.com.mx/api/payment')
            elif self.company_id.proveedor_timbrado == 'multifactura3':
                url = '%s' % ('http://facturacion3.itadmin.com.mx/api/payment')
            elif self.company_id.proveedor_timbrado == 'gecoerp':
                if self.company_id.modo_prueba:
                    #url = '%s' % ('https://ws.gecoerp.com/itadmin/pruebas/payment/?handler=OdooHandler33')
                    url = '%s' % ('https://itadmin.gecoerp.com/payment2/?handler=OdooHandler33')
                else:
                    url = '%s' % ('https://itadmin.gecoerp.com/payment2/?handler=OdooHandler33')
            try:
                response = requests.post(url , 
                                     auth=None,verify=False, data=json.dumps(values), 
                                     headers={"Content-type": "application/json"})
            except Exception as e:
                error = str(e)
                if "Name or service not known" in error or "Failed to establish a new connection" in error:
                     raise Warning("Servidor fuera de servicio, favor de intentar mas tarde")
                else:
                     raise Warning(error)

            if "Whoops, looks like something went wrong." in response.text:
                raise Warning("Error en el proceso de timbrado, espere un minuto y vuelva a intentar timbrar nuevamente. \nSi el error aparece varias veces reportarlo con la persona de sistemas.")
            else:
                json_response = response.json()
            xml_file_link = False
            estado_pago = json_response['estado_pago']
            if estado_pago == 'problemas_pago':
                raise UserError(_(json_response['problemas_message']))
            # Receive and stroe XML 
            if json_response.get('pago_xml'):
                xml_file_link = p.company_id.factura_dir + '/' + p.name.replace('/', '_') + '.xml'
                xml_file = open(xml_file_link, 'w')
                xml_payment = base64.b64decode(json_response['pago_xml'])
                xml_file.write(xml_payment.decode("utf-8"))
                xml_file.close()
                p._set_data_from_xml(xml_payment)
                    
                xml_file_name = p.name.replace('/', '_') + '.xml'
                self.env['ir.attachment'].sudo().create(
                                            {
                                                'name': xml_file_name,
                                                'datas': json_response['pago_xml'],
                                                'datas_fname': xml_file_name,
                                                'res_model': self._name,
                                                'res_id': p.id,
                                                'type': 'binary'
                                            })
                report = self.env['ir.actions.report']._get_report_from_name('cdfi_invoice.report_payment')
                report_data = report.render_qweb_pdf([p.id])[0]
                pdf_file_name = p.name.replace('/', '_') + '.pdf'
                self.env['ir.attachment'].sudo().create(
                                            {
                                                'name': pdf_file_name,
                                                'datas': base64.b64encode(report_data),
                                                'datas_fname': pdf_file_name,
                                                'res_model': self._name,
                                                'res_id': p.id,
                                                'type': 'binary'
                                            })

            p.write({'estado_pago': estado_pago,
                    'xml_payment_link': xml_file_link})
            p.message_post(body="CFDI emitido")
            
    @api.multi
    def validate_complete_payment(self):
        self.post()
        return {
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }

    @api.one
    def _set_data_from_xml(self, xml_payment):
        if not xml_payment:
            return None
        NSMAP = {
                 'xsi':'http://www.w3.org/2001/XMLSchema-instance',
                 'cfdi':'http://www.sat.gob.mx/cfd/4', 
                 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
                 'pago20': 'http://www.sat.gob.mx/Pagos20',
                 }
        xml_data = etree.fromstring(xml_payment)
        Complemento = xml_data.find('cfdi:Complemento', NSMAP)
        TimbreFiscalDigital = Complemento.find('tfd:TimbreFiscalDigital', NSMAP)

        self.numero_cetificado = xml_data.attrib['NoCertificado']
        self.fecha_emision = xml_data.attrib['Fecha']
        self.cetificaso_sat = TimbreFiscalDigital.attrib['NoCertificadoSAT']
        self.fecha_certificacion = TimbreFiscalDigital.attrib['FechaTimbrado']
        self.selo_digital_cdfi = TimbreFiscalDigital.attrib['SelloCFD']
        self.selo_sat = TimbreFiscalDigital.attrib['SelloSAT']
        self.folio_fiscal = TimbreFiscalDigital.attrib['UUID']
        self.folio = xml_data.attrib['Folio']     
        version = TimbreFiscalDigital.attrib['Version']
        self.cadena_origenal = '||%s|%s|%s|%s|%s||' % (version, self.folio_fiscal, self.fecha_certificacion, 
                                                         self.selo_digital_cdfi, self.cetificaso_sat)
        
        options = {'width': 275 * mm, 'height': 275 * mm}
        amount_str = str(self.amount).split('.')
        qr_value = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?&id=%s&re=%s&rr=%s&tt=%s.%s&fe=%s' % (self.folio_fiscal,
                                                 self.company_id.rfc, 
                                                 self.partner_id.rfc,
                                                 amount_str[0].zfill(10),
                                                 amount_str[1].ljust(6, '0'),
                                                 self.selo_digital_cdfi[-8:],
                                                 )
        self.qr_value = qr_value
        ret_val = createBarcodeDrawing('QR', value=qr_value, **options)
        self.qrcode_image = base64.encodestring(ret_val.asString('jpg'))
        #self.folio_fiscal = TimbreFiscalDigital.attrib['UUID']

    @api.multi
    def send_payment(self):
        self.ensure_one()
        template = self.env.ref('cdfi_invoice.email_template_payment', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
            
        ctx = dict()
        ctx.update({
            'default_model': 'account.payment',
            'default_res_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_cfdi_cancel(self):
        for p in self:
            #if invoice.factura_cfdi:
                if p.estado_pago == 'factura_cancelada':
                    pass
                    # raise UserError(_('La factura ya fue cancelada, no puede volver a cancelarse.'))
                if not p.company_id.archivo_cer:
                    raise UserError(_('Falta la ruta del archivo .cer'))
                if not p.company_id.archivo_key:
                    raise UserError(_('Falta la ruta del archivo .key'))
                archivo_cer = p.company_id.archivo_cer.decode("utf-8")
                archivo_key = p.company_id.archivo_key.decode("utf-8")
                archivo_xml_link = p.company_id.factura_dir + '/' + p.name.replace('/', '_') + '.xml'
                with open(archivo_xml_link, 'rb') as cf:
                     archivo_xml = base64.b64encode(cf.read())
                values = {
                          'rfc': p.company_id.rfc,
                          'api_key': p.company_id.proveedor_timbrado,
                          'uuid': p.folio_fiscal,
                          'folio': p.folio,
                          'serie_factura': p.company_id.serie_complemento,
                          'modo_prueba': p.company_id.modo_prueba,
                            'certificados': {
                                  'archivo_cer': archivo_cer,
                                  'archivo_key': archivo_key,
                                  'contrasena': p.company_id.contrasena,
                            },
                          'xml': archivo_xml.decode("utf-8"),
                          'motivo': self.env.context.get('motivo_cancelacion','02'),
                          'foliosustitucion': self.env.context.get('foliosustitucion',''),
                          }
                if p.company_id.proveedor_timbrado == 'multifactura':
                    url = '%s' % ('http://facturacion.itadmin.com.mx/api/refund')
                elif p.company_id.proveedor_timbrado == 'multifactura2':
                    url = '%s' % ('http://facturacion2.itadmin.com.mx/api/refund')
                elif p.company_id.proveedor_timbrado == 'multifactura3':
                    url = '%s' % ('http://facturacion3.itadmin.com.mx/api/refund')
                elif p.company_id.proveedor_timbrado == 'gecoerp':
                    if p.company_id.modo_prueba:
                         #url = '%s' % ('https://ws.gecoerp.com/itadmin/pruebas/refund/?handler=OdooHandler33')
                        url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                    else:
                        url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                response = requests.post(url , 
                                         auth=None,verify=False, data=json.dumps(values), 
                                         headers={"Content-type": "application/json"})

                json_response = response.json()
                
                if json_response['estado_factura'] == 'problemas_factura':
                    raise UserError(_(json_response['problemas_message']))
                elif json_response.get('factura_xml', False):
                    if p.name:
                        xml_file_link = p.company_id.factura_dir + '/CANCEL_' + p.name.replace('/', '_') + '.xml'
                    else:
                        xml_file_link = p.company_id.factura_dir + '/CANCEL_' + p.folio + '.xml'
                    xml_file = open(xml_file_link, 'w')
                    xml_invoice = base64.b64decode(json_response['factura_xml'])
                    xml_file.write(xml_invoice.decode("utf-8"))
                    xml_file.close()
                    if p.name:
                        file_name = p.name.replace('/', '_') + '.xml'
                    else:
                        file_name = p.folio + '.xml'
                    self.env['ir.attachment'].sudo().create(
                                                {
                                                    'name': file_name,
                                                    'datas': json_response['factura_xml'],
                                                    'datas_fname': file_name,
                                                    'res_model': self._name,
                                                    'res_id': p.id,
                                                    'type': 'binary'
                                                })
                p.write({'estado_pago': json_response['estado_factura']})
                p.message_post(body="CFDI Cancelado")

    def truncate(self, number, decimals=0):
        """
        Returns a value truncated to a specific number of decimal places.
        """
        if not isinstance(decimals, int):
            raise TypeError("decimal places must be an integer.")
        elif decimals < 0:
            raise ValueError("decimal places has to be 0 or more.")
        elif decimals == 0:
            return math.trunc(number)

        factor = 10.0 ** decimals
        return math.trunc(number * factor) / factor

class AccountPaymentMail(models.Model):
    _name = "account.payment.mail"
    _inherit = ['mail.thread']
    _description = "Payment Mail"
    
    payment_id = fields.Many2one('account.payment', string='Payment')
    name = fields.Char(related='payment_id.name')
    xml_payment_link = fields.Char(related='payment_id.xml_payment_link')
    partner_id = fields.Many2one(related='payment_id.partner_id')
    company_id = fields.Many2one(related='payment_id.company_id')
    
class MailTemplate(models.Model):
    "Templates for sending email"
    _inherit = 'mail.template'
    
    @api.model
    def _get_file(self, url):
        url = url.encode('utf8')
        filename, headers = urllib.urlretrieve(url)
        fn, file_extension = os.path.splitext(filename)
        return  filename, file_extension.replace('.', '')

    @api.multi
    def generate_email(self, res_ids, fields=None):
        results = super(MailTemplate, self).generate_email(res_ids, fields=fields)
        
        if isinstance(res_ids, (int)):
            res_ids = [res_ids]
        res_ids_to_templates = super(MailTemplate, self).get_email_template(res_ids)

        # templates: res_id -> template; template -> res_ids
        templates_to_res_ids = {}
        for res_id, template in res_ids_to_templates.items():
            templates_to_res_ids.setdefault(template, []).append(res_id)
        
        template_id = self.env.ref('cdfi_invoice.email_template_payment')
        for template, template_res_ids in templates_to_res_ids.items():
            if template.id  == template_id.id:
                for res_id in template_res_ids:
                    payment = self.env[template.model].browse(res_id)
                    if payment.xml_payment_link:
                        attachments =  results[res_id]['attachments'] or []
                        names = payment.xml_payment_link.split('/')
                        fn = names[len(names) - 1]
                        data = open(payment.xml_payment_link, 'rb').read()
                        attachments.append((fn, base64.b64encode(data)))
                        results[res_id]['attachments'] = attachments
        return results

class AccountPaymentTerm(models.Model):
    "Terminos de pago"
    _inherit = "account.payment.term"

    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
                   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), 
    )

    forma_pago = fields.Selection(
        selection=[('01', '01 - Efectivo'), 
                   ('02', '02 - Cheque nominativo'), 
                   ('03', '03 - Transferencia electrónica de fondos'),
                   ('04', '04 - Tarjeta de Crédito'), 
                   ('05', '05 - Monedero electrónico'),
                   ('06', '06 - Dinero electrónico'), 
                   ('08', '08 - Vales de despensa'), 
                   ('12', '12 - Dación en pago'), 
                   ('13', '13 - Pago por subrogación'), 
                   ('14', '14 - Pago por consignación'), 
                   ('15', '15 - Condonación'), 
                   ('17', '17 - Compensación'), 
                   ('23', '23 - Novación'), 
                   ('24', '24 - Confusión'), 
                   ('25', '25 - Remisión de deuda'), 
                   ('26', '26 - Prescripción o caducidad'), 
                   ('27', '27 - A satisfacción del acreedor'), 
                   ('28', '28 - Tarjeta de débito'), 
                   ('29', '29 - Tarjeta de servicios'), 
                   ('30', '30 - Aplicación de anticipos'),
                   ('31', '31 - Intermediario pagos'),
                   ('99', '99 - Por definir'),],
        string=_('Forma de pago'),
    )
