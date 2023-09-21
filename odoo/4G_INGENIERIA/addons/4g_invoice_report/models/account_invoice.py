# -*- coding: utf-8 -*-

from odoo import fields, models, api,_ 
from reportlab.graphics.barcode import createBarcodeDrawing
import base64
from lxml import etree
from reportlab.lib.units import mm

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    rfc_emisor = fields.Char(string=_('RFC'))
    name_emisor = fields.Char(string=_('Name'))
    no_compra = fields.Char('Orden de compra cliente', compute='_get_no_compra')
    @api.model
    def _get_no_compra(self):
        if self.origin:
            so = self.env['sale.order'].search([('name', '=', self.origin)])
            if so:
               self.no_compra = so[0].no_compra

    @api.one
    def _set_data_from_xml(self, xml_invoice):
        if not xml_invoice:
            return None
        NSMAP = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
        }

        xml_data = etree.fromstring(xml_invoice)
        Complemento = xml_data.findall('cfdi:Complemento', NSMAP)

        for complementos in Complemento:
            TimbreFiscalDigital = complementos.find('tfd:TimbreFiscalDigital', NSMAP)
            if TimbreFiscalDigital:
                break

        self.total_factura = xml_data.attrib['Total']
        self.tipocambio = xml_data.attrib['TipoCambio']
        self.moneda = xml_data.attrib['Moneda']
        self.numero_cetificado = xml_data.attrib['NoCertificado']
        self.cetificaso_sat = TimbreFiscalDigital.attrib['NoCertificadoSAT']
        self.fecha_certificacion = TimbreFiscalDigital.attrib['FechaTimbrado']
        self.selo_digital_cdfi = TimbreFiscalDigital.attrib['SelloCFD']
        self.selo_sat = TimbreFiscalDigital.attrib['SelloSAT']
        self.folio_fiscal = TimbreFiscalDigital.attrib['UUID']
        self.invoice_datetime = xml_data.attrib['Fecha']

        ##Modulo Aparte
        Emisor = xml_data.find('cfdi:Emisor', NSMAP)
        self.rfc_emisor = Emisor.attrib['Rfc']
        self.name_emisor = Emisor.attrib['Nombre']   
        
             
#        if not self.fecha_factura:
#            self.fecha_factura = self.invoice_datetime.replace('T', ' ')
        version = TimbreFiscalDigital.attrib['Version']
        self.cadena_origenal = '||%s|%s|%s|%s|%s||' % (version, self.folio_fiscal, self.fecha_certificacion,
                                                       self.selo_digital_cdfi, self.cetificaso_sat)

        options = {'width': 275 * mm, 'height': 275 * mm}
        amount_str = str(self.amount_total).split('.')
        qr_value = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?&id=%s&re=%s&rr=%s&tt=%s.%s&fe=%s' % (
            self.folio_fiscal,
            self.company_id.rfc,
            self.partner_id.rfc,
            amount_str[0].zfill(10),
            amount_str[1].ljust(6, '0'),
            self.selo_digital_cdfi[-8:],
        )
        self.qr_value = qr_value
        ret_val = createBarcodeDrawing('QR', value=qr_value, **options)
        self.qrcode_image = base64.encodestring(ret_val.asString('jpg'))





