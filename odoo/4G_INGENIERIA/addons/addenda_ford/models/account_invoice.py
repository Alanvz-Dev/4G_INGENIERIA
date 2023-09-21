# -*- coding: utf-8 -*-

from odoo import fields, models, api 
import os
import io
import logging
_logger = logging.getLogger(__name__)
from lxml import etree
from dateutil.parser import parse

data = """<cfdi:Addenda>
    <fomadd:addenda xmlns:fomadd="http://www.ford.com.mx/cfdi/addenda" xsi:schemaLocation="http://www.ford.com.mx/cfdi/addenda http://www.ford.com.mx/cfdi/addenda/cfdiAddendaFord_1_0.xsd">
       <fomadd:FOMASN version="1.0">
            <fomadd:GSDB>%s</fomadd:GSDB>
"""

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    ford_agregado = fields.Boolean(string='Addenda Ford escrita', default=False, readonly=True)
    ford_addenda = fields.Boolean(string='Addenda Ford', default=False)

    @api.multi
    def add_addenda_ford(self):
        self.addenda_ford()
        return True

    @api.multi
    def addenda_ford(self):
        tfd_namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}

        for invoice in self:
            if invoice.xml_invoice_link and os.path.exists(invoice.xml_invoice_link) and not invoice.ford_agregado:
                try:
                    new_data = data%(self.company_id.ford_gsdb)
                    secuencia = ""
                    for line in self.invoice_line_ids: 
                        secuencia +="""
           <fomadd:ASN>%s</fomadd:ASN>"""%(line.product_id.default_code)
                    new_data2 = """
      </fomadd:FOMASN>
    </fomadd:addenda>
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
                        invoice.ford_agregado = True
                except Exception as e:
                    _logger.error(str(e))
                    pass