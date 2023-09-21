# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
#import odoo.addons.decimal_precision as dp
import os
import io
import logging
_logger = logging.getLogger(__name__)
from lxml import etree
from dateutil.parser import parse

data_ppy = """ <cfdi:Addenda>
    <factura version="1.0" tipoDocumento="%s" montoTotal="%s" folioFiscal="%s" fecha="%s" TipoDocumentoFiscal="FA">
       <moneda tipoMoneda="%s" />
       <proveedor codigo="%s" nombre="%s" />
       <destino codigo="%s" nombre="%s" />
       <otrosCargos codigo="V6" monto="%s" />
       <partes>
"""
data_pua = """ <cfdi:Addenda>
    <factura version="1.0" tipoDocumento="%s" referenciaProveedor="%s" montoTotal="%s" folioFiscal="%s" serie="%s" fecha="%s" TipoDocumentoFiscal="FA">
       <moneda tipoMoneda="%s" />
       <proveedor codigo="%s" nombre="%s" />
       <destino codigo="%s" nombre="%s" />
       <otrosCargos codigo="V6" monto="%s" />
       <partes>
"""

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    codigo_envio = fields.Many2one('addenda.chrysler.envio', string='Dirección de envío')
    orden_compra = fields.Char(string='Orden de compra')
    requicision_liberacion = fields.Char(string='Requisición de liberación')
    chrysler_addenda = fields.Boolean(string='Addenda Chrysler', default=False)
    chrysler_agregado = fields.Boolean(string='Addenda Chrysler escrita', default=False, readonly=True)
    fca_tipodocumento = fields.Selection(
        selection=[('PUA', 'PUA'), 
                   ('PPY', 'PPY'),],
        string=_('Tipo de documento'),
    )

    @api.multi
    def add_addenda_chrysler(self):
        self.addenda_chrysler()
        return True

    @api.multi
    def addenda_chrysler(self):
        tfd_namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}

        for invoice in self:
            if invoice.xml_invoice_link and os.path.exists(invoice.xml_invoice_link) and not invoice.chrysler_agregado:
                try:
                    if self.fca_tipodocumento == 'PUA':
                        if self.moneda == 'MXN':
                           new_data = data_pua%(self.fca_tipodocumento, self.serie_emisor +''+'FV'+self.number_folio, self.amount_total, self.number_folio, self.serie_emisor, self.date_invoice, self.moneda,
                                   self.company_id.chrysler_no_proveedor, self.company_id.name , self.codigo_envio.envio_codigo, self.codigo_envio.envio_nombre, self.amount_tax)
                        else:
                           new_data = data_pua%(self.fca_tipodocumento, self.serie_emisor +''+self.number_folio, self.amount_total, self.number_folio, self.serie_emisor, self.date_invoice, self.moneda + 
                                    '" tipoCambio="'+self.tipocambio, self.company_id.chrysler_no_proveedor, self.company_id.name, self.codigo_envio.envio_codigo, 
                                     self.codigo_envio.envio_nombre, self.amount_tax)
                    else:
                        if self.moneda == 'MXN':
                           new_data = data_ppy%(self.fca_tipodocumento, self.amount_total, self.number_folio, self.date_invoice, self.moneda, self.company_id.chrysler_no_proveedor,
                                    self.company_id.name, self.codigo_envio.envio_codigo, self.codigo_envio.envio_nombre, self.amount_tax)
                        else:
                           new_data = data_ppy%(self.fca_tipodocumento, self.amount_total, self.number_folio, self.date_invoice, self.moneda + '" tipoCambio="'+self.tipocambio,
                                   self.company_id.chrysler_no_proveedor, self.company_id.name, self.codigo_envio.envio_codigo, self.codigo_envio.envio_nombre, self.amount_tax)
                    secuencia = ""
                    for line in self.invoice_line_ids:
                         if line.no_parte:
                           secuencia +="""
            <part cantidad="%s" numero="%s" unidadDeMedida="%s" precioUnitario="%s" montoDeLinea="%s" >
                <references ammendment="%s" releaseRequisicion="%s" ordenCompra="%s" />
            </part>"""%(line.quantity, line.no_parte, line.product_id.uom_id.name, line.price_unit, line.price_subtotal, line.line_item, self.requicision_liberacion, self.orden_compra)
                         else:
                           secuencia +="""
            <part cantidad="%s" unidadDeMedida="%s" precioUnitario="%s" montoDeLinea="%s" >
                <references ammendment="%s" releaseRequisicion="%s" ordenCompra="%s" />
            </part>"""%(line.quantity, line.product_id.uom_id.name, line.price_unit, line.price_subtotal, line.line_item, self.requicision_liberacion, self.orden_compra)

                    new_data2 = """
       </partes>
    </factura>
 </cfdi:Addenda>
</cfdi:Comprobante>
"""
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
                        invoice.chrysler_agregado = True
#                     f = open(invoice.xml_invoice_link,'a+')
#                     f.write(new_data)
#                     f.close()
                except Exception as e:
                    _logger.error(str(e))
                    pass