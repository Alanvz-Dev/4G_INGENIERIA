# -*- coding: utf-8 -*-

import base64
import json
import requests

from lxml import etree

from odoo import fields, models, api,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, Warning
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import mm
from . import amount_to_text_es_MX
import pytz
from .tzlocal import get_localzone
from odoo import tools

import logging
_logger = logging.getLogger(__name__)
import datetime
class CfdiTrasladoLine(models.Model):
    _name = "cfdi.traslado.line"
    
    cfdi_traslado_id= fields.Many2one('cfdi.traslado',string="CFDI Traslado")
    product_id = fields.Many2one('product.product',string='Producto',required=True)
    name = fields.Text(string='Descripción',required=True,)
    quantity = fields.Float(string='Cantidad', digits=dp.get_precision('Unidad de medida del producto'),required=True, default=1)
    price_unit = fields.Float(string='Precio unitario', required=True, digits=dp.get_precision('Product Price'))
    invoice_line_tax_ids = fields.Many2many('account.tax',string='Taxes')
    currency_id = fields.Many2one('res.currency', related='cfdi_traslado_id.currency_id', store=True, related_sudo=False, readonly=False)
    price_subtotal = fields.Monetary(string='Subtotal',
        store=True, readonly=True, compute='_compute_price', help="Subtotal")
    price_total = fields.Monetary(string='Cantidad (con Impuestos)',
        store=True, readonly=True, compute='_compute_price', help="Cantidad total con impuestos")
    pesoenkg = fields.Float(string='Peso Kg', digits=dp.get_precision('Product Price'))
    pedimento = fields.Many2many('stock.production.lot', string='Pedimentos', copy=False)
    guiaid_numero = fields.Char(string=_('No. Guia'))
    guiaid_descrip = fields.Char(string=_('Descr. guia'))
    guiaid_peso = fields.Float(string='Peso guia')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self.name = self.product_id.partner_ref
        company_id = self.env.user.company_id
        taxes = self.product_id.taxes_id.filtered(lambda r: r.company_id == company_id)
        self.invoice_line_tax_ids = fp_taxes = taxes
        fix_price = self.env['account.tax']._fix_tax_included_price
        self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)
        self.pesoenkg = self.product_id.weight

    @api.depends('price_unit', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'cfdi_traslado_id.partner_id', 'cfdi_traslado_id.currency_id',)
    def _compute_price(self):
        for line in self:
            currency = line.cfdi_traslado_id and line.cfdi_traslado_id.currency_id or None
            price = line.price_unit
            taxes = False
            if line.invoice_line_tax_ids:
                taxes = line.invoice_line_tax_ids.compute_all(price, currency, line.quantity, product=line.product_id, partner=line.cfdi_traslado_id.partner_id)
            line.price_subtotal = taxes['total_excluded'] if taxes else line.quantity * price
            line.price_total = taxes['total_included'] if taxes else line.price_subtotal

    @api.onchange('quantity')
    def _onchange_quantity(self):
        self.pesoenkg = self.product_id.weight * self.quantity

class CCPUbicacionesLine(models.Model):
    _name = "ccp.ubicaciones.line"
    
    cfdi_traslado_id= fields.Many2one('cfdi.traslado',string="CFDI Traslado")
    tipoubicacion = fields.Selection(
        selection=[('Origen', 'Origen'), 
                   ('Destino', 'Destino'),],
        string=_('Tipo Ubicación'), required=True
    )
    contacto = fields.Many2one('res.partner',string="Remitente / Destinatario", required=True)
    numestacion = fields.Many2one('cve.estaciones',string='Número de estación')
    fecha = fields.Datetime(string=_('Fecha Salida / Llegada'), required=True)
    tipoestacion = fields.Many2one('cve.estacion',string='Tipo estación')
    distanciarecorrida = fields.Float(string='Distancia recorrida')
    tipo_transporte = fields.Selection(
        selection=[('01', 'Autotransporte'), 
                  # ('02', 'Marítimo'), 
                   ('03', 'Aereo'),
                   #('04', 'Ferroviario')
                  ],
        string=_('Tipo de transporte')
    )
    idubicacion = fields.Char(string=_('ID Ubicacion'))

class CCPRemolqueLine(models.Model):
    _name = "ccp.remolques.line"

    cfdi_traslado_id= fields.Many2one('cfdi.traslado',string="CFDI Traslado")
    subtipo_id = fields.Many2one('cve.remolque.semiremolque',string="Subtipo")
    placa = fields.Char(string=_('Placa'))

class CCPPropietariosLine(models.Model):
    _name = "ccp.figura.line"

    cfdi_traslado_id= fields.Many2one('cfdi.traslado',string="CFDI Traslado")
    figura_id = fields.Many2one('res.partner',string="Contacto")
    tipofigura = fields.Many2one('cve.figura.transporte',string="Tipo figura")
    partetransporte = fields.Many2many('cve.parte.transporte',string="Parte transporte")

class CfdiTraslado(models.Model):
    _name = "cfdi.traslado"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "number"

    factura_cfdi = fields.Boolean('Factura CFDI')
    number = fields.Char(string="Numero", store=True, readonly=True, copy=False,
                         default=lambda self: _('Factura borrador'))
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('valid', 'Validada'),
        ('cancel', 'Cancelada'),
    ], string='Status', index=True, readonly=True, default='draft', )

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
        string=_('Forma de pago')
    )
    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
                   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), 
    )
    uso_cfdi = fields.Selection(
        selection=[('G01', _('Adquisición de mercancías')),
                   ('G02', _('Devoluciones, descuentos o bonificaciones')),
                   ('G03', _('Gastos en general')),
                   ('I01', _('Construcciones')),
                   ('I02', _('Mobiliario y equipo de oficina por inversiones')),
                   ('I03', _('Equipo de transporte')),
                   ('I04', _('Equipo de cómputo y accesorios')),
                   ('I05', _('Dados, troqueles, moldes, matrices y herramental')),
                   ('I06', _('Comunicacion telefónica')),
                   ('I07', _('Comunicación Satelital')),
                   ('I08', _('Otra maquinaria y equipo')),
                   ('D01', _('Honorarios médicos, dentales y gastos hospitalarios')),
                   ('D02', _('Gastos médicos por incapacidad o discapacidad')),
                   ('D03', _('Gastos funerales')),
                   ('D04', _('Donativos')),
                   ('D05', _('Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación).')),
                   ('D06', _('Aportaciones voluntarias al SAR.')),
                   ('D07', _('Primas por seguros de gastos médicos')),
                   ('D08', _('Gastos de transportación escolar obligatoria')),
                   ('D09', _('Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones')),
                   ('D10', _('Pagos por servicios educativos (colegiaturas)')),
                   ('S01', _('Sin efectos fiscales')),
                   ('P01', _('Por definir (obsoleto)')),],
        string=_('Uso CFDI (cliente)'),
        default = 'S01',
    )

    tipo_comprobante = fields.Selection(
        selection=[('I', 'Ingreso'),
                   ('E', 'Egreso'),
                   ('T', 'Traslado'),],
        string=_('Tipo de comprobante'),default='T',
    )
    folio_fiscal = fields.Char(string=_('Folio Fiscal'), readonly=True)
    confirmacion = fields.Char(string=_('Confirmación'))
    estado_factura = fields.Selection(
        selection=[('factura_no_generada', 'Factura no generada'), ('factura_correcta', 'Factura correcta'),
                   ('solicitud_cancelar', 'Cancelación en proceso'), ('factura_cancelada', 'Factura cancelada'),
                   ('solicitud_rechazada', 'Cancelación rechazada'), ],
        string=_('Estado de factura'),
        default='factura_no_generada',
        readonly=True
    )
    fecha_factura = fields.Datetime(string=_('Fecha Factura'))
    tipo_relacion = fields.Selection(
        selection=[('01', 'Nota de crédito de los documentos relacionados'),
                   ('02', 'Nota de débito de los documentos relacionados'),
                   ('03', 'Devolución de mercancía sobre facturas o traslados previos'),
                   ('04', 'Sustitución de los CFDI previos'),
                   ('05', 'Traslados de mercancías facturados previamente'),
                   ('06', 'Factura generada por los traslados previos'),
                   ('07', 'CFDI por aplicación de anticipo')],
        string=_('Tipo relación')
    )

    uuid_relacionado = fields.Char(string=_('CFDI Relacionado'))
    xml_invoice_link = fields.Char(string=_('XML Invoice Link'))
    qr_value = fields.Char(string=_('QR Code Value'))
    qrcode_image = fields.Binary("QRCode")
    comment = fields.Text("Comentario")
    partner_id = fields.Many2one('res.partner', string="Cliente", required=True, default=lambda self: self.env.user.company_id.id)
    source_document = fields.Char(string="Documento origen")
    invoice_date = fields.Datetime(string="Fecha de factura")
    factura_line_ids = fields.One2many('cfdi.traslado.line', 'cfdi_traslado_id', string='CFDI Traslado Line', copy=True)
    currency_id = fields.Many2one('res.currency',string='Moneda',default=lambda self: self.env['res.company']._company_default_get('cfdi.traslado').currency_id, required=True)
    amount_untaxed = fields.Float(string='Untaxed Amount', store=True, readonly=True, default=0)
    amount_tax = fields.Float(string='Tax', store=True, readonly=True, default=0)
    amount_total = fields.Float(string='Total', store=True, readonly=True, default=0)

    numero_cetificado = fields.Char(string=_('Numero de cetificado'))
    cetificaso_sat = fields.Char(string=_('Cetificao SAT'))
    fecha_certificacion = fields.Char(string=_('Fecha y Hora Certificación'))
    cadena_origenal = fields.Char(string=_('Cadena Origenal del Complemento digital de SAT'))
    selo_digital_cdfi = fields.Char(string=_('Selo Digital del CDFI'))
    selo_sat = fields.Char(string=_('Selo del SAT'))
    moneda = fields.Char(string=_('Moneda'))
    tipocambio = fields.Char(string=_('TipoCambio'))
    #folio = fields.Char(string=_('Folio'))
    #version = fields.Char(string=_('Version'))
    number_folio = fields.Char(string=_('Folio'), compute='_get_number_folio')
    amount_to_text = fields.Char('Amount to Text', compute='_get_amount_to_text',
                                 size=256, 
                                 help='Amount of the invoice in letter')
    qr_value = fields.Char(string=_('QR Code Value'))
    invoice_datetime = fields.Char(string=_('11/12/17 12:34:12'))
    proceso_timbrado = fields.Boolean(string=_('Proceso de timbrado'))
    rfc_emisor = fields.Char(string=_('RFC'))
    name_emisor = fields.Char(string=_('Name'))
    serie_emisor = fields.Char(string=_('A'))

    decimales = fields.Float(string='decimales')
    company_id = fields.Many2one('res.company', 'Compañia',
                                 default=lambda self: self.env['res.company']._company_default_get('cfdi.traslado'))

    tipo_transporte = fields.Selection(
        selection=[('01', 'Autotransporte'), 
                  # ('02', 'Marítimo'), 
                   ('03', 'Aereo'),
                  # ('04', 'Ferroviario')
                  ],
        string=_('Tipo de transporte'),required=True, default='01'
    )
    carta_porte = fields.Boolean('Agregar carta porte', default = True)

    ##### atributos CP 
    transpinternac = fields.Selection(
        selection=[('Sí', 'Si'), 
                   ('No', 'No'),],
        string=_('¿Es un transporte internacional?'),default='No',
    )
    entradasalidamerc = fields.Selection(
        selection=[('Entrada', 'Entrada'), 
                   ('Salida', 'Salida'),],
        string=_('¿Las mercancías ingresan o salen del territorio nacional?'),
    )
    viaentradasalida = fields.Many2one('cve.transporte',string='Vía de ingreso / salida')
    totaldistrec = fields.Float(string='Distancia recorrida')

    ##### ubicaciones CP
    ubicaciones_line_ids = fields.One2many('ccp.ubicaciones.line', 'cfdi_traslado_id', string='Ubicaciones', copy=True)

    ##### mercancias CP
    pesobrutototal = fields.Float(string='Peso bruto total', compute='_compute_pesobruto')
    unidadpeso = fields.Many2one('cve.clave.unidad',string='Unidad peso')
    pesonetototal = fields.Float(string='Peso neto total')
    numerototalmercancias = fields.Float(string='Numero total de mercancías', compute='_compute_mercancia')
    cargoportasacion = fields.Float(string='Cargo por tasación')

    #transporte
    permisosct = fields.Many2one('cve.tipo.permiso',string='Permiso SCT')
    numpermisosct = fields.Char(string=_('Número de permiso SCT'))

    #autotransporte
    autotrasporte_ids = fields.Many2one('ccp.autotransporte',string='Unidad')
    remolque_line_ids = fields.One2many('ccp.remolques.line', 'cfdi_traslado_id', string='Remolque', copy=True)
    nombreaseg_merc = fields.Char(string=_('Nombre de la aseguradora'))
    numpoliza_merc = fields.Char(string=_('Número de póliza'))
    primaseguro_merc = fields.Float(string=_('Prima del seguro'))
    seguro_ambiente = fields.Char(string=_('Nombre aseguradora'))
    poliza_ambiente = fields.Char(string=_('Póliza no.'))

    ##### Aereo CP
    numeroguia = fields.Char(string=_('Número de guía'))
    lugarcontrato = fields.Char(string=_('Lugar de contrato'))
    matriculaaeronave = fields.Char(string=_('Matrícula Aeronave'))
    transportista_id = fields.Many2one('res.partner',string="Transportista")
    embarcador_id = fields.Many2one('res.partner',string="Embarcador")

    uuidcomercioext = fields.Char(string=_('UUID Comercio Exterior'))
    paisorigendestino = fields.Many2one('catalogos.paises', string='País Origen / Destino')

    # figura transporte
    figuratransporte_ids = fields.One2many('ccp.figura.line', 'cfdi_traslado_id', string='Seguro mercancías', copy=True)

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if self.estado_factura == 'factura_correcta' or self.estado_factura == 'factura_cancelada':
            default['estado_factura'] = 'factura_no_generada'
            default['folio_fiscal'] = ''
            default['fecha_factura'] = None
            default['factura_cfdi'] = False
        return super(CfdiTraslado, self).copy(default=default)

    @api.depends('number')
    @api.one
    def _get_number_folio(self):
        if self.number:
            self.number_folio = self.number.replace('CT','').replace('/','')

    @api.model
    def _get_amount_2_text(self, amount_total):
        return amount_to_text_es_MX.get_amount_to_text(self, amount_total, 'es_cheque', self.currency_id.name)

    @api.model
    def _default_journal(self):
        company_id = self.env['res.company']._company_default_get('cfdi.traslado')
        if not self.journal_id:
            return self.env['account.journal'].search([('type', '=', 'sale'),('company_id', '=', company_id.id)], limit=1)

    journal_id = fields.Many2one('account.journal', 'Diario', default=_default_journal)

    @api.model
    def create(self, vals):
        if vals.get('number', _('Draft Invoice')) == _('Draft Invoice'):
            if 'company_id' in vals:
                vals['number'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('cfdi.traslado') or _('Draft Invoice')
            else:
                vals['number'] = self.env['ir.sequence'].next_by_code('cfdi.traslado') or _('Draft Invoice')
        result = super(CfdiTraslado, self).create(vals)
        return result

    def action_valid(self):
        self.write({'state': 'valid'})
        self.invoice_date = datetime.datetime.now()

    def action_set_draft(self):
        self.write({'state':'draft'})
        
    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.onchange('factura_line_ids')
    def _compute_pesobruto(self):
        peso = 0
        if self.factura_line_ids:
            for line in self.factura_line_ids:
               peso += line.pesoenkg
        self.pesobrutototal = peso
        self.pesonetototal = peso

    @api.onchange('factura_line_ids')
    def _compute_mercancia(self):
        cant = 0
        for rec in self:
            if rec.factura_line_ids:
                for line in rec.factura_line_ids:
                    cant += 1
            rec.numerototalmercancias = cant


    @api.model
    def to_json(self):
        if self.partner_id.rfc == 'XAXX010101000':
            nombre = 'PUBLICO EN GENERAL'
        else:
            nombre = self.partner_id.name.upper()

        no_decimales = self.currency_id.no_decimales
        no_decimales_prod = self.currency_id.decimal_places
        no_decimales_tc = self.currency_id.no_decimales_tc

        #corregir hora
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.journal_id.tz or self.env.user.partner_id.tz or 'America/Mexico_City'
        # timezone = tools.ustr(timezone).encode('utf-8')

        local = pytz.timezone(timezone)
        if not self.fecha_factura:
           naive_from = datetime.datetime.now()
        else:
           naive_from =datetime.datetime.strptime(self.fecha_factura, '%Y-%m-%d %H:%M:%S') 
        local_dt_from = naive_from.replace(tzinfo=pytz.UTC).astimezone(local)
        date_from = local_dt_from.strftime ("%Y-%m-%dT%H:%M:%S")
        if not self.fecha_factura:
           self.fecha_factura = datetime.datetime.now()

        request_params = {
                'factura': {
                      'serie': self.journal_id.serie_diario or self.company_id.serie_factura,
                      'folio': self.number.replace('CT','').replace('/',''),
                      'fecha_expedicion': date_from,
                     # 'forma_pago':'',
                      'subtotal': self.amount_untaxed,
                     # 'descuento': 0,
                      'moneda': 'XXX',
                     # 'tipocambio': tipocambio,
                      'total': self.amount_total,
                      'tipocomprobante': self.tipo_comprobante,
                      'metodo_pago': self.methodo_pago,
                      'LugarExpedicion': self.journal_id.codigo_postal or self.company_id.zip,
                      'Confirmacion': self.confirmacion,
                      'Exportacion': '01',
                },
                'emisor': {
                      'rfc': self.company_id.rfc.upper(),
                      'nombre': self.company_id.nombre_fiscal.upper(),
                      'RegimenFiscal': self.company_id.regimen_fiscal,
                      #'FacAtrAdquirente': self.facatradquirente,
                },
                'receptor': {
                      'nombre': nombre,
                      'rfc': self.partner_id.rfc.upper(),
                      'ResidenciaFiscal': self.partner_id.residencia_fiscal,
                      'NumRegIdTrib': self.partner_id.registro_tributario,
                      'UsoCFDI': self.uso_cfdi,
                      'RegimenFiscalReceptor': self.partner_id.regimen_fiscal,
                      'DomicilioFiscalReceptor': self.partner_id.zip,
                },
                'informacion': {
                      'cfdi': '4.0',
                      'sistema': 'odoo11',
                      'version': '2',
                      'api_key': self.company_id.proveedor_timbrado,
                      'modo_prueba': self.company_id.modo_prueba,
                },
        }

        items = {'numerodepartidas': len(self.factura_line_ids)}
        invoice_lines = []
        for line in self.factura_line_ids:
                invoice_lines.append({'cantidad': self.set_decimals(line.quantity,6),
                                      'unidad': line.product_id.unidad_medida,
                                      'NoIdentificacion': line.product_id.default_code,
                                      'valorunitario': self.set_decimals(line.price_unit, no_decimales_prod),
                                      'importe': self.set_decimals(line.price_unit * line.quantity, no_decimales_prod),
                                      'descripcion': self.clean_text(line.product_id.name),
                                      'ClaveProdServ': line.product_id.clave_producto,
                                      'ObjetoImp': '01',
                                      'ClaveUnidad': line.product_id.clave_unidad})

        request_params['factura'].update({'subtotal': '0','total': '0'})

        request_params.update({'conceptos': invoice_lines})

        return request_params

    def set_decimals(self, amount, precision):
        if amount is None or amount is False:
            return None
        return '%.*f' % (precision, amount)

    def clean_text(self, text):
        clean_text = text.replace('\n', ' ').replace('\\', ' ').replace('-', ' ').replace('/', ' ').replace('|', ' ')
        clean_text = clean_text.replace(',', ' ').replace(';', ' ').replace('>', ' ').replace('<', ' ')
        return clean_text[:1000]

    def check_cfdi_values(self):
        if not self.company_id.rfc:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('El emisor no tiene RFC configurado.'))
        if not self.company_id.name:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('El emisor no tiene nombre configurado.'))
        if not self.partner_id.rfc:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('El receptor no tiene RFC configurado.'))
        if not self.uso_cfdi:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('La factura no tiene uso de cfdi configurado.'))
        if not self.tipo_comprobante:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('El emisor no tiene tipo de comprobante configurado.'))
        if self.tipo_comprobante != 'T' and not self.methodo_pago:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('La factura no tiene método de pago configurado.'))
        if self.tipo_comprobante != 'T' and not self.forma_pago:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('La factura no tiene forma de pago configurado.'))
        if not self.company_id.regimen_fiscal:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('El emisor no régimen fiscal configurado.'))
        if not self.journal_id.codigo_postal and not self.company_id.zip:
            self.write({'proceso_timbrado': False})
            self.env.cr.commit()
            raise UserError(_('El emisor no tiene código postal configurado.'))

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

        #self.tipocambio = xml_data.attrib['TipoCambio']
        self.moneda = xml_data.attrib['Moneda']
        self.numero_cetificado = xml_data.attrib['NoCertificado']
        self.cetificaso_sat = TimbreFiscalDigital.attrib['NoCertificadoSAT']
        self.fecha_certificacion = TimbreFiscalDigital.attrib['FechaTimbrado']
        self.selo_digital_cdfi = TimbreFiscalDigital.attrib['SelloCFD']
        self.selo_sat = TimbreFiscalDigital.attrib['SelloSAT']
        self.folio_fiscal = TimbreFiscalDigital.attrib['UUID']
        self.invoice_datetime = xml_data.attrib['Fecha']
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

    ################################################################################################################
    ###############################  Adicional de Complemento de traslado ##########################################
    ################################################################################################################
    @api.model
    def to_json_carta_porte(self, request_params):
        res =  request_params
        self.totaldistrec = 0

        #cartaporte20 = []
        cp_ubicacion = []
        #cp_mercancias = []
        for ubicacion in self.ubicaciones_line_ids:

            #corregir hora
            timezone = self._context.get('tz')
            if not timezone:
               timezone = self.journal_id.tz or self.env.user.partner_id.tz or 'America/Mexico_City'
            local = pytz.timezone(timezone)

            new_date = datetime.datetime.strptime(ubicacion.fecha, "%Y-%m-%d %H:%M:%S")
            local_dt_from = new_date.replace(tzinfo=pytz.UTC).astimezone(local)
            date_fecha = local_dt_from.strftime ("%Y-%m-%dT%H:%M:%S")
            self.totaldistrec += float(ubicacion.distanciarecorrida)
            _logger.info('totaldistrec %s', self.totaldistrec)

            cp_ubicacion.append({
                            'TipoUbicacion': ubicacion.tipoubicacion,
                          # 'IDUbicacion': ubicacion.origen_id,
                            'RFCRemitenteDestinatario': ubicacion.contacto.rfc,
                            'NombreRemitenteDestinatario': ubicacion.contacto.name,
                            'NumRegIdTrib': ubicacion.contacto.registro_tributario,
                            'ResidenciaFiscal': ubicacion.contacto.residencia_fiscal,
                            'NumEstacion': self.tipo_transporte != '01' and ubicacion.numestacion.clave_identificacion or '',
                            'NombreEstacion': self.tipo_transporte != '01' and ubicacion.numestacion.descripcion or '',
                          # 'NavegacionTrafico': self.company_id.zip,
                            'FechaHoraSalidaLlegada': date_fecha,
                            'TipoEstacion': self.tipo_transporte != '01' and ubicacion.tipoestacion.c_estacion or '',
                            'DistanciaRecorrida': ubicacion.distanciarecorrida > 0 and ubicacion.distanciarecorrida or '',
                            'Domicilio': {
                                'Calle': ubicacion.contacto.cce_calle,
                                'NumeroExterior': ubicacion.contacto.cce_no_exterior,
                                'NumeroInterior': ubicacion.contacto.cce_no_interior,
                                'Colonia': ubicacion.contacto.cce_clave_colonia.c_colonia,
                                'Localidad': ubicacion.contacto.cce_clave_localidad.c_localidad,
                          #      'Referencia': self.company_id.cce_clave_estado.c_estado,
                                'Municipio': ubicacion.contacto.cce_clave_municipio.c_municipio,
                                'Estado': ubicacion.contacto.cce_clave_estado.c_estado,
                                'Pais': ubicacion.contacto.cce_clave_pais.c_pais,
                                'CodigoPostal': ubicacion.contacto.zip,
                            },
                         })

        #################  Atributos y Ubicacion ############################
   #     if self.tipo_transporte == '01' or self.tipo_transporte == '04':
        cartaporte20= {'TranspInternac': self.transpinternac,
                       'EntradaSalidaMerc': self.entradasalidamerc,
                       'ViaEntradaSalida': self.viaentradasalida.c_transporte,
                       'TotalDistRec': self.tipo_transporte == '01' and self.totaldistrec or '',
                       'PaisOrigenDestino': self.paisorigendestino.c_pais,
                      }
  #      else:
  #          res.update({
  #                   'cartaporte': {
  #                          'TranspInternac': self.transpinternac,
  #                          'EntradaSalidaMerc': self.entradasalidamerc,
  #                          'ViaEntradaSalida': self.viaentradasalida.c_transporte,
  #                          'TipoTransporte': self.tipo_transporte,
  #                   },
  #              })

        cartaporte20.update({'Ubicaciones': cp_ubicacion})

        #################  Mercancias ############################
        mercancias = { 
                       'PesoBrutoTotal': self.pesobrutototal, #solo si es aereo o ferroviario
                       'UnidadPeso': self.unidadpeso.clave,
                       'PesoNetoTotal': self.pesonetototal if self.pesonetototal > 0 else '',
                       'NumTotalMercancias': self.numerototalmercancias,
                       'CargoPorTasacion': self.cargoportasacion if self.cargoportasacion > 0 else '',
        }

        mercancia = []
        for line in self.factura_line_ids:
            if line.quantity <= 0:
                continue
            mercancia_atributos = {
                            'BienesTransp': line.product_id.clave_producto,
                            'ClaveSTCC': line.product_id.clave_stcc,
                            'Descripcion': self.clean_text(line.product_id.name),
                            'Cantidad': line.quantity,
                            'ClaveUnidad': line.product_id.clave_unidad,
                            'Unidad': line.product_id.unidad_medida,
                            'Dimensiones': line.product_id.dimensiones,
                            'MaterialPeligroso': line.product_id.materialpeligroso,
                            'CveMaterialPeligroso': line.product_id.clavematpeligroso.clave,
                            'Embalaje': line.product_id.embalaje and line.product_id.embalaje.clave or '',
                            'DescripEmbalaje': line.product_id.desc_embalaje and line.product_id.desc_embalaje or '',
                            'PesoEnKg': line.pesoenkg,
                            'ValorMercancia': line.price_subtotal,
                            'Moneda': self.currency_id.name,
                            'FraccionArancelaria': line.product_id.fraccion_arancelaria and line.product_id.fraccion_arancelaria.c_fraccionarancelaria or '',
                            'UUIDComercioExt': self.uuidcomercioext,
            }
            pedimentos = []
            if line.pedimento:
               for no_pedimento in line.pedimento:
                  pedimentos.append({
                                 'Pedimento': no_pedimento.name[:2] + '  ' + no_pedimento.name[2:4] + '  ' + no_pedimento.name[4:8] + '  ' + no_pedimento.name[8:],
                  })
            guias = [] # soo si tiene un dato
            if line.guiaid_numero:
               guias.append({
                          'NumeroGuiaIdentificacion': line.guiaid_numero,
                          'DescripGuiaIdentificacion': line.guiaid_descrip,
                          'PesoGuiaIdentificacion': line.guiaid_peso,
               })

        #################  CantidadTransporta ############################
        #################  pueden haber varios revisar ############################
   #     mercancia_cantidadt = {
   #                         'Cantidad': merc.product_id.code,
   #                         'IDOrigen': merc.fraccionarancelaria.c_fraccionarancelaria,
   #                         'IDDestino': merc.cantidadaduana,
   #                       #  'CvesTransporte': merc.valorunitarioaduana,
   #     })
		
        #################  DetalleMercancia ############################
      #  mercancia_detalle = {
      #                      'UnidadPesoMerc': merc.product_id.code,
      #                      'PesoBruto': merc.fraccionarancelaria.c_fraccionarancelaria,
      #                      'PesoNeto': merc.cantidadaduana,
      #                      'PesoTara': merc.valorunitarioaduana,
      #                      'NumPiezas': merc.valordolares,
      #  }


#           mercancia.update({'mercancia_cantidadt': mercancia_cantidadt})
#           mercancia.update({'mercancia_detalle': mercancia_detalle})
            mercancia.append({'atributos': mercancia_atributos, 'Pedimentos': pedimentos, 'GuiasIdentificacion': guias})
        mercancias.update({'mercancia': mercancia})

        if self.tipo_transporte == '01': #autotransporte
              transpote_detalle = {
                            'PermSCT': self.permisosct.clave,
                            'NumPermisoSCT': self.numpermisosct,
                            'IdentificacionVehicular': {
                                 'ConfigVehicular': self.autotrasporte_ids.confvehicular.clave,
                                 'PlacaVM': self.autotrasporte_ids.placavm,
                                 'AnioModeloVM': self.autotrasporte_ids.aniomodelo,
                            },
                            'Seguros': {
                                 'AseguraRespCivil': self.autotrasporte_ids.nombreaseg,
                                 'PolizaRespCivil': self.autotrasporte_ids.numpoliza,
                                 'AseguraCarga': self.nombreaseg_merc,
                                 'PolizaCarga': self.numpoliza_merc,
                                 'PrimaSeguro': self.primaseguro_merc,
                                 'AseguraMedAmbiente': self.seguro_ambiente,
                                 'PolizaMedAmbiente': self.poliza_ambiente,
                            },
              }
              remolques = []
              if self.remolque_line_ids:
                 for remolque in self.remolque_line_ids:
                     remolques.append({
                            'SubTipoRem': remolque.subtipo_id.clave,
                            'Placa': remolque.placa,
                     })
                 transpote_detalle.update({'Remolques': remolques})

              mercancias.update({'Autotransporte': transpote_detalle})
        elif self.tipo_transporte == '02': # maritimo
              maritimo = []
        elif self.tipo_transporte == '03': #aereo
              transpote_detalle = {
                            'PermSCT': self.permisosct.clave,
                            'NumPermisoSCT': self.numpermisosct,
                            'MatriculaAeronave': self.matriculaaeronave,
                         #   'NombreAseg': self.nombreaseg,  ******
                         #   'NumPolizaSeguro': self.numpoliza, *****
                            'NumeroGuia': self.numeroguia,
                            'LugarContrato': self.lugarcontrato,
                            'CodigoTransportista': self.transportista_id.codigotransportista.clave,
                            'RFCEmbarcador': self.embarcador_id.rfc if self.embarcador_id.cce_clave_pais.c_pais == 'MEX' else '',
                            'NumRegIdTribEmbarc': self.embarcador_id.registro_tributario,
                            'ResidenciaFiscalEmbarc': self.embarcador_id.cce_clave_pais.c_pais if self.embarcador_id.cce_clave_pais.c_pais != 'MEX' else '',
                            'NombreEmbarcador': self.embarcador_id.name,
              }
              mercancias.update({'TransporteAereo': transpote_detalle})
        elif self.tipo_transporte == '04': #ferroviario
              ferroviario = []

        cartaporte20.update({'Mercancias': mercancias})

        #################  Figura transporte ############################
        figuratransporte = []
        tipos_figura = []
        for figura in self.figuratransporte_ids:
            tipos_figura = {
                       'TipoFigura': figura.tipofigura.clave,
                       'RFCFigura': figura.figura_id.rfc if figura.figura_id.cce_clave_pais.c_pais == 'MEX' else '',
                       'NumLicencia': figura.figura_id.cce_licencia,
                       'NombreFigura': figura.figura_id.name,
                       'NumRegIdTribFigura': figura.figura_id.registro_tributario,
                       'ResidenciaFiscalFigura': figura.figura_id.cce_clave_pais.c_pais if figura.figura_id.cce_clave_pais.c_pais != 'MEX' else '',
                       'Domicilio': {
                                'Calle': figura.figura_id.cce_calle,
                                'NumeroExterior': figura.figura_id.cce_no_exterior,
                                'NumeroInterior': figura.figura_id.cce_no_interior,
                                'Colonia': figura.figura_id.cce_clave_colonia.c_colonia,
                                'Localidad': figura.figura_id.cce_clave_localidad.c_localidad,
                          #      'Referencia': operador.company_id.cce_clave_estado.c_estado,
                                'Municipio': figura.figura_id.cce_clave_municipio.c_municipio,
                                'Estado': figura.figura_id.cce_clave_estado.c_estado,
                                'Pais': figura.figura_id.cce_clave_pais.c_pais,
                                'CodigoPostal': figura.figura_id.zip,
                       },
            }

            partes = []
            for parte in figura.partetransporte:
               partes.append({
                    'ParteTransporte': parte.clave,
               })
            figuratransporte.append({'TiposFigura': tipos_figura, 'PartesTransporte': partes})

        cartaporte20.update({'FiguraTransporte': figuratransporte})
        res.update({'cartaporte20': cartaporte20})

        return res

    @api.multi
    def action_cfdi_generate(self):
        # after validate, send invoice data to external system via http post
        for invoice in self:
            if invoice.proceso_timbrado:
                return True
            else:
               invoice.write({'proceso_timbrado': True})
               self.env.cr.commit()
            if invoice.estado_factura == 'factura_correcta':
                if invoice.folio_fiscal:
                    invoice.write({'factura_cfdi': True})
                    return True
                else:
                    invoice.write({'proceso_timbrado': False})
                    self.env.cr.commit()
                    raise UserError(_('Error para timbrar factura, Factura ya generada.'))
            if invoice.estado_factura == 'factura_cancelada':
                invoice.write({'proceso_timbrado': False})
                self.env.cr.commit()
                raise UserError(_('Error para timbrar factura, Factura ya generada y cancelada.'))

            values = invoice.to_json()
            if self.carta_porte:
                 values = invoice.to_json_carta_porte(values)
            if invoice.company_id.proveedor_timbrado == 'multifactura':
                url = '%s' % ('http://facturacion.itadmin.com.mx/api/invoice')
            elif invoice.company_id.proveedor_timbrado == 'multifactura2':
                url = '%s' % ('http://facturacion2.itadmin.com.mx/api/invoice')
            elif invoice.company_id.proveedor_timbrado == 'multifactura3':
                url = '%s' % ('http://facturacion3.itadmin.com.mx/api/invoice')
            elif invoice.company_id.proveedor_timbrado == 'gecoerp':
                if self.company_id.modo_prueba:
                    url = '%s' % ('https://itadmin.gecoerp.com/invoice/?handler=OdooHandler33')
                else:
                    url = '%s' % ('https://itadmin.gecoerp.com/invoice/?handler=OdooHandler33')
            else:
                invoice.write({'proceso_timbrado': False})
                self.env.cr.commit()
                raise UserError(_('Error, falta seleccionar el servidor de timbrado en la configuración de la compañía.'))

            try:
                response = requests.post(url,
                                         auth=None, verify=False, data=json.dumps(values),
                                         headers={"Content-type": "application/json"})
            except Exception as e:
                error = str(e)
                invoice.write({'proceso_timbrado': False})
                self.env.cr.commit()
                if "Name or service not known" in error or "Failed to establish a new connection" in error:
                    raise Warning("No se pudo conectar con el servidor.")
                else:
                    raise Warning(error)

            if "Whoops, looks like something went wrong." in response.text:
                invoice.write({'proceso_timbrado': False})
                self.env.cr.commit()
                raise Warning("Error en el proceso de timbrado, espere un minuto y vuelva a intentar timbrar nuevamente. \nSi el error aparece varias veces reportarlo con la persona de sistemas.")
            else:
                json_response = response.json()
            estado_factura = json_response['estado_factura']
            if estado_factura == 'problemas_factura':
                invoice.write({'proceso_timbrado': False})
                self.env.cr.commit()
                raise UserError(_(json_response['problemas_message']))
            # Receive and stroe XML invoice
            if json_response.get('factura_xml'):
                xml_file_link = invoice.company_id.factura_dir + '/' + invoice.number.replace('/', '_') + '.xml'
                xml_file = open(xml_file_link, 'w')
                xml_invoice = base64.b64decode(json_response['factura_xml'])
                xml_file.write(xml_invoice.decode("utf-8"))
                xml_file.close()
                invoice._set_data_from_xml(xml_invoice)
            invoice.write({'estado_factura': estado_factura,
                           'xml_invoice_link': xml_file_link,
                           'factura_cfdi': True,
                           'proceso_timbrado': False})
            #invoice.message_post(body="CFDI emitido")
        return True

    @api.multi
    def action_cfdi_cancel(self):
        for invoice in self:
            if invoice.factura_cfdi:
                if invoice.estado_factura == 'factura_cancelada':
                    pass
                    # raise UserError(_('La factura ya fue cancelada, no puede volver a cancelarse.'))
                #if not invoice.company_id.archivo_cer:
                #    raise UserError(_('Falta la ruta del archivo .cer'))
                #if not invoice.company_id.archivo_key:
                #    raise UserError(_('Falta la ruta del archivo .key'))
                #archivo_cer = self.company_id.archivo_cer
                #archivo_key = self.company_id.archivo_key
                archivo_xml_link = invoice.company_id.factura_dir + '/' + invoice.number.replace('/', '_') + '.xml'
                with open(archivo_xml_link, 'rb') as cf:
                     archivo_xml = base64.b64encode(cf.read())
                values = {
                    'rfc': invoice.company_id.rfc,
                    'api_key': invoice.company_id.proveedor_timbrado,
                    'uuid': invoice.folio_fiscal,
                    'folio': invoice.number.replace('CT','').replace('/',''),
                    'serie_factura': invoice.journal_id.serie_diario or invoice.company_id.serie_factura,
                    'modo_prueba': invoice.company_id.modo_prueba,
                    'certificados': {
                    #    'archivo_cer': archivo_cer.decode("utf-8"),
                    #    'archivo_key': archivo_key.decode("utf-8"),
                        'contrasena': invoice.company_id.contrasena,
                    },
                    'xml': archivo_xml.decode("utf-8"),
                    'motivo': self.env.context.get('motivo_cancelacion',False),
                    'foliosustitucion': self.env.context.get('foliosustitucion',''),
                }
                if self.company_id.proveedor_timbrado == 'multifactura':
                    url = '%s' % ('http://facturacion.itadmin.com.mx/api/refund')
                elif invoice.company_id.proveedor_timbrado == 'multifactura2':
                    url = '%s' % ('http://facturacion2.itadmin.com.mx/api/refund')
                elif invoice.company_id.proveedor_timbrado == 'multifactura3':
                    url = '%s' % ('http://facturacion3.itadmin.com.mx/api/refund')
                elif self.company_id.proveedor_timbrado == 'gecoerp':
                    if self.company_id.modo_prueba:
                        url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                    else:
                        url = '%s' % ('https://itadmin.gecoerp.com/refund/?handler=OdooHandler33')
                else:
                    raise UserError(_('Error, falta seleccionar el servidor de timbrado en la configuración de la compañía.'))

                try:
                    response = requests.post(url,
                                             auth=None, verify=False, data=json.dumps(values),
                                             headers={"Content-type": "application/json"})
                except Exception as e:
                    error = str(e)
                    if "Name or service not known" in error or "Failed to establish a new connection" in error:
                        raise Warning("No se pudo conectar con el servidor.")
                    else:
                        raise Warning(error)

                if "Whoops, looks like something went wrong." in response.text:
                    raise Warning("Error en el proceso de timbrado, espere un minuto y vuelva a intentar timbrar nuevamente. \nSi el error aparece varias veces reportarlo con la persona de sistemas.")

                json_response = response.json()

                log_msg = ''
                if json_response['estado_factura'] == 'problemas_factura':
                    raise UserError(_(json_response['problemas_message']))
                elif json_response['estado_factura'] == 'solicitud_cancelar':
                    # invoice.write({'estado_factura': json_response['estado_factura']})
                    log_msg = "Se solicitó cancelación de CFDI"
                    # raise Warning(_(json_response['problemas_message']))
                elif json_response.get('factura_xml', False):
                    if invoice.number:
                        xml_file_link = invoice.company_id.factura_dir + '/CANCEL_' + invoice.number.replace('/', '_') + '.xml'
                    else:
                        xml_file_link = invoice.company_id.factura_dir + '/CANCEL_' + invoice.move_name.replace('/', '_') + '.xml'
                    xml_file = open(xml_file_link, 'w')
                    xml_invoice = base64.b64decode(json_response['factura_xml'])
                    xml_file.write(xml_invoice.decode("utf-8"))
                    xml_file.close()
                    if invoice.number:
                        file_name = invoice.number.replace('/', '_') + '.xml'
                    else:
                        file_name = invoice.move_name.replace('/', '_') + '.xml'
                    self.env['ir.attachment'].sudo().create(
                        {
                            'name': file_name,
                            'datas': json_response['factura_xml'],
                            'datas_fname': file_name,
                            'res_model': self._name,
                            'res_id': invoice.id,
                            'type': 'binary'
                        })
                    log_msg = "CFDI Cancelado"
                invoice.write({'estado_factura': json_response['estado_factura']})
                # invoice.message_post(body=log_msg)
   
    def send_factura_mail(self):
        self.ensure_one()
        template = self.env.ref('cfdi_traslado.email_template_factura_traslado', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
            
        ctx = dict()
        ctx.update({
            'default_model': 'cfdi.traslado',
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

    def unlink(self):
        raise UserError("Los registros no se pueden borrar, solo cancelar.")

class CfdiTrasladoMail(models.Model):
    _name = "cfdi.traslado.mail"
    _inherit = ['mail.thread']
    _description = "CFDI Traslado Mail"

    factura_id = fields.Many2one('cfdi.traslado', string='CFDI Traslado')
    name = fields.Char(related='factura_id.number')
    xml_invoice_link = fields.Char(related='factura_id.xml_invoice_link')
    partner_id = fields.Many2one(related='factura_id.partner_id')
    company_id = fields.Many2one(related='factura_id.company_id')


class MailTemplate(models.Model):
    "Templates for sending email"
    _inherit = 'mail.template'

    @api.model
    def _get_file(self, url):
        url = url.encode('utf8')
        filename, headers = urllib.urlretrieve(url)
        fn, file_extension = os.path.splitext(filename)
        return filename, file_extension.replace('.', '')

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

        template_id = self.env.ref('cfdi_traslado.email_template_factura_traslado')
        for template, template_res_ids in templates_to_res_ids.items():
            if template.id  == template_id.id:
                for res_id in template_res_ids:
                    factura = self.env[template.model].browse(res_id)
                    if factura.xml_invoice_link:
                        attachments =  results[res_id]['attachments'] or []
                        names = factura.xml_invoice_link.split('/')
                        fn = names[len(names) - 1]
                        data = open(factura.xml_invoice_link, 'rb').read()
                        attachments.append((fn, base64.b64encode(data)))
                        results[res_id]['attachments'] = attachments
        return results

