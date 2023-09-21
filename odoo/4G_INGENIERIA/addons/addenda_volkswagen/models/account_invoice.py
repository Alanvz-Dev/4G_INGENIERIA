# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
#import odoo.addons.decimal_precision as dp
import os
import io
import logging
_logger = logging.getLogger(__name__)
from lxml import etree
from dateutil.parser import parse

data = """<cfdi:Addenda>
  <PMT:Factura version="1.0" tipoDocumentoVWM="PMT" division="VW" tipoDocumentoFiscal="FA" xmlns:PMT="http://www.vwnovedades.com/volkswagen/kanseilab/shcp/2009/Addenda/PMT">
  <PMT:Moneda tipoMoneda="%s" tipoCambio="%s" CodigoImpuesto="1A"/>
  <PMT:Proveedor codigo="%s" nombre="%s"/>
  <PMT:Destino codigo="%s"/>
  <PMT:Referencias referenciaProveedor="%s" remision="%s"/>
  <PMT:Partes>"""

data2 = """ <cfdi:Addenda>
  <PSV:Factura version="1.0" tipoDocumentoVWM="PSV" division="VW" tipoDocumentoFiscal="FA" xmlns:PSV="http://www.vwnovedades.com/volkswagen/kanseilab/shcp/2009/Addenda/PSV">
  <PSV:Moneda tipoMoneda="%s" CodigoImpuesto="1A"/>
  <PSV:Proveedor codigo="%s" nombre="%s" correoContacto="%s"/>
  <PSV:Referencias remision="%s"/>
  <PSV:Solicitante correo="%s" nombre="%s"/>
  <PSV:Archivo datos="%" tipo="PDF"/>
  <PSV:Partes>"""

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    de_codigo = fields.Char()
    vw_posicion = fields.Char(string='No. Posicion VW')
    vw_odc = fields.Char(string='Orden de compra VW')
    vw_contacto = fields.Many2one('addenda.vw.contacto', string='Contacto Addenda')
    vw_notas = fields.Char(string='Notas VW')
    vw_pdf = fields.Binary(string=_('Remision PDF'))
    vw_agregado = fields.Boolean(string='Addenda VW Escrita', default=False, readonly=True)
    vw_addenda = fields.Boolean(string='Addenda VW Materiales', default=False)

    @api.multi
    def add_addenda_volkswagen(self):
        self.addenda_volkswagen()
        return True

    @api.multi
    def addenda_volkswagen(self):
        tfd_namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}

        for invoice in self:
            if invoice.xml_invoice_link and os.path.exists(invoice.xml_invoice_link) and not invoice.vw_agregado:
                try:
                    if self.vw_pdf:
                       new_data = data2%( self.moneda, self.company_id.vw_no_proveedor, self.company_id.name, self.company_id.vw_correo,
                           self.folio_fiscal, self.vw_contacto.contacto_mail, self.vw_contacto.contacto_nombre, self.vw_pdf)
                    else:
                       new_data = data%( self.moneda, self.tipocambio, self.partner_id.ref, self.partner_id.name,
                           self.de_codigo, self.company_id.vw_no_proveedor, self.serie_emisor +''+self.folio)
                    #posicion = 0
                    secuencia = ""
                    for line in self.invoice_line_ids: 
                        secuencia +="""    <PMT:Parte posicion="%s" numeroMaterial="%s" descripcionMaterial="%s"  cantidadMaterial="%s" unidaDeMedida="%s" precioUnitario="%s" montoDeLinea="%s">
       <PMT:Referencias ordenCompra="%s"/>
    </PMT:Parte>
"""%(self.vw_posicion, line.product_id.default_code, line.name, line.quantity, line.product_id.uom_id.name, line.price_unit, line.price_subtotal, self.vw_odc)
                    new_data2 = """  </PMT:Partes>
  </PMT:Factura>
 </cfdi:Addenda>
</cfdi:Comprobante>"""

                    filedata = ''
                    # Read in the file
                    with io.open(invoice.xml_invoice_link, 'r', encoding='utf-8') as f:
                        filedata = f.read()
                    
                    # Replace the target string    
                    filedata = filedata.replace('</cfdi:Comprobante>', new_data)
                    filedata2 = secuencia
                    filedata3 = new_data2
                    # Write the file out again
                    with io.open(invoice.xml_invoice_link, 'w', encoding='utf-8') as f:
                        f.write(filedata)
                        f.write(filedata2)
                        f.write(filedata3)
                        invoice.vw_agregado = True
#                     f = open(invoice.xml_invoice_link,'a+')
#                     f.write(new_data)
#                     f.close()
                except Exception as e:
                    _logger.error(str(e))
                    pass