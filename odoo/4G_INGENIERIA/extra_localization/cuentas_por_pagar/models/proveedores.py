# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import base64
import xml.dom.minidom
from datetime import datetime, timedelta

from cfdiclient import Validacion



class cxp_proveedores(models.Model):

    _name = 'cuentas_por_pagar.proveedor.model'
    _description = 'Cuentas Por Pagar'
    _rec_name = 'invoice_select_name'




    @api.model
    def _get_partner(self):
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        partner_ids=[]
        if user_br.partner_id.id:
            partner_ids.append(user_br.partner_id.id)
        if user_br.partner_id.parent_id.id:
            partner_ids.append(user_br.partner_id.parent_id.id)
        self.env['account.invoice'].validate_cdp(partner_ids)
        return user_br.partner_id.id

    @api.one
    @api.depends('rfc')
    def _compute_search_ids(self):
        print('View My Department CLO ACL')
        
    @api.multi
    def search_ids_search1(self,operator,operand):
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        rfc = user_br.partner_id.vat
        partner = self.env['res.partner']
        partner_ids = partner.search([('vat', 'ilike', rfc)]).ids        
        obj = self.env['cuentas_por_pagar.proveedor.model'].search([('partner_id', 'in', partner_ids)]).ids        
        return [('id', 'in', obj)]


    search_ids = fields.Char(
        compute="_compute_search_ids", search='search_ids_search1')


    @api.model
    def _get_reference_invoice_(self):
        invoice = self.env['account.invoice']
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        rfc = user_br.partner_id.vat
        partner = self.env['res.partner']
        partner_ids = partner.search([('vat', 'ilike', rfc)])
        partner_ids = [x.id for x in partner_ids]
        if user != 1:        
            invoice_ids = invoice.search([('partner_id', 'in',
                                           tuple(partner_ids)), ('type', '=', 'in_invoice'),
                                          ('state', 'in', ('open', )),('state_files', 'in', ('pending', ))])
            # invoice_ids_without_attachments=self.env['ir.attachment'].search([('res_id','not in',tuple(invoice_ids)),('res_model','=','account.invoice')])
            # print(invoice_ids_without_attachments)
        else:
            invoice_ids = invoice.search([('type', '=', 'in_invoice'),
                                          ('state', 'in', ('open', )),('state_files', 'in', ('pending', ))])
        #    without_attachments=invoice_ids
        #     without_attachments=[]
        #     for itemx in invoice_ids:   
        #         attachments=self.env['ir.attachment'].search([('res_id','=',(itemx.id))])
        #         if not attachments:
        #             without_attachments.append(itemx.id)
        # print(without_attachments)
        # invoice_ids = invoice.search([('id', '=', tuple(without_attachments))])        
        selection = []
        if invoice_ids:
            for inv in invoice_ids:
                invoice_subs_name = 'Factura: ' + str(inv.reference) \
                    + ' - ' + 'OC: ' + str(inv.origin) + ' - ' \
                    + 'Factura Monto: ' + '/' + str(inv.amount_total)
                xval = (inv.id, invoice_subs_name)
                selection.append(xval)
        return selection

    partner_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        readonly=True,
        change_default=True,
        track_visibility='always',
        default=_get_partner,
    )

      

    fecha_pago = fields.Char(store=True)
    rfc = fields.Char('RFC', related='partner_id.vat', readonly=True,
                      size=13)
    phone = fields.Char('Telefono', related='partner_id.phone',
                        readonly=True)
    email = fields.Char(string='Correo', related='partner_id.email',
                        readonly=True)
    modified_by_user=fields.Boolean(default=False)
    fecha = fields.Datetime(
        'Fecha:',
        required=True,
        index=True,
        readonly=True,
        copy=False,
        default=fields.Datetime.now,
        help='Representa la fecha en la que se crea el archivo.',
    )
    STATES = [('draft', 'Borrador'), ('done','Abrir')]
    state = fields.Selection(selection=lambda self: self._compute_selection(),store=True)


    @api.multi
    def _compute_selection(self):
        payment_mode = [('done','Abrir')]
        return payment_mode

    

    xml = fields.Binary(string='Archivo XML', required=True)
    xmlname = fields.Char()

    pdf = fields.Binary(string='Archivo PDF', required=True)
    pdfname = fields.Char()

    invoice_id = fields.Many2one('account.invoice', 'Factura')

    invoice_select = fields.Selection('_get_reference_invoice_',
                                      string='No. Factura', store=True)

    invoice_select_name = fields.Char('Ref. Factura')

    file_one = fields.Binary(string='Archivo')
    file_one_name = fields.Char(string='Archivo')


    _order = 'partner_id'

    _defaults = {'name': '', 'state': 'draft'}

    @api.one
    @api.constrains('xmlname')
    def _check_xmlname(self):
        if not self.xml:
            raise UserError(_('No hay Archivo'))
        if self.xmlname.endswith('.xml') == False:
            raise UserError(_('El archivo debe ser XML'))

    @api.one
    @api.constrains('pdfname')
    def _check_pdfname(self):
        if not self.pdf:
            raise UserError(_('No hay Archivo'))
        if self.pdfname.endswith('.pdf') == False:
            raise UserError(_('El archivo debe ser PDF'))

#Valida que corresponda el monto, referencia y otros datos de la factura
    @api.one
    @api.constrains('xml')
    def _validate_xml_file(self):
        
        invoice = self.env['account.invoice']        
        invoice_br=invoice.search([('id','=',self.invoice_select)])
        document=base64.decodestring(self.xml)
        dom = xml.dom.minidom.parseString(document)    

        nodos = dom.childNodes
        x = nodos[0].attributes.get('Version').value 
        y = nodos[0].attributes.get('Fecha').value 
        formato = "%Y-%m-%dT%H:%M:%S"
        fecha_objeto = datetime.strptime(y, formato)
        
        

        if x == '3.3':
            if  fecha_objeto > datetime(2023, 3, 31):
                raise UserError(_('Debido a la disposiciones del SAT y la entrada en vigor del CFDI 4.0 se les informa que toda factura que no venga en este formato será rechazada del portal de proveedores hasta no ser detectada con el timbrado correcto (CFDI 4.0). Cabe resaltar que esto será aplicado con las facturas que tengan fecha de timbrado posterior al 1° de abril 2023 %s %s')%(fecha_objeto,datetime(2023, 3, 1)))
            
        print(x)
        rfc_emisor=nodos[0].getElementsByTagName('cfdi:Emisor')[0].attributes.get('Rfc').value
        rfc_receptor=nodos[0].getElementsByTagName('cfdi:Receptor')[0].attributes.get('Rfc').value
        total = float(nodos[0].attributes.get('Total').value)
        if total  ==0:
            raise UserError(_('La factura no puede estar en 0, asegurese que no sea un complemento de pago y comuniquese con su comprador lo antes posible.'))
        days_of_payment_due=''
        validacion = Validacion()
        uuid=nodos[0].getElementsByTagName('tfd:TimbreFiscalDigital')[0].attributes.get('UUID').value
        payment_term_id=''
        try:
            #print(invoice_br.commercial_partner_id.property_payment_term_id.id)
            #print(invoice_br.commercial_partner_id.property_supplier_payment_term_id.id)
            if invoice_br.commercial_partner_id.property_supplier_payment_term_id.id:
                if not invoice_br.commercial_partner_id.property_supplier_payment_term_id.id:
                    raise UserError(_('No tiene configurado el plazo de pago, por favor comuniquese a 4G para que se lo asignen.'))

                payment_term_id=invoice_br.commercial_partner_id.property_supplier_payment_term_id.id
        
            self._cr.execute('select name from account_payment_term where id='+str(payment_term_id))
            gg=self.env.cr.fetchall()
            str_days_of_payment_due=list(gg[0][0])
        except:
             raise UserError(_('No tiene configurado el plazo de pago, por favor comuniquese a 4G para que se lo asignen.'))
        
            
        for i in range(len(str_days_of_payment_due)):
            r=str_days_of_payment_due[i]
            print(str_days_of_payment_due[i])
            if str_days_of_payment_due[i] =='1' or str_days_of_payment_due[i]=='3' or str_days_of_payment_due[i]=='4' or str_days_of_payment_due[i]=='5' or str_days_of_payment_due[i]=='6' or str_days_of_payment_due[i]=='7' or str_days_of_payment_due[i]=='8' or str_days_of_payment_due[i]=='9' or str_days_of_payment_due[i]=='0':
                days_of_payment_due=days_of_payment_due+str_days_of_payment_due[i]
        
        if False==(invoice_br.amount_total>=(total-1) and  invoice_br.amount_total<=(total+1)):
            raise UserError(_('Las cantidades no coinciden entre su factura xml y la Orden de compra'))
        if invoice_br.partner_id.vat != rfc_emisor:
            raise UserError(_('El RFC del emisor no coincide entre su factura xml y la Orden de compra'))
        print(days_of_payment_due)
        print((datetime.now()+timedelta(days=int(days_of_payment_due))).strftime("%Y-%m-%d"))

        estado_sat={}
        try:
            estado_sat = validacion.obtener_estado(rfc_emisor, rfc_receptor, str(total), uuid)            
        except:
            pass
        #     raise UserError(_('Los servicios SAT no se encuentran disponibles por el momento, por favor intente más tarde.'))
        # if not estado_sat.get('estado')=='Vigente':
        #     raise UserError(_('Error SAT: '+str(estado_sat)))
        
        invoice_br.sudo().write({'date_due':(datetime.now()+timedelta(days=int(days_of_payment_due))).strftime("%Y-%m-%d")})
        invoice_br.sudo().write({'state_files':'uploaded'})
        attachment_xml={
                            'res_id': invoice_br.id,
                            'res_model': 'account.invoice',
                            'name': (self.xmlname),
                            'db_datas': self.xml,
                            'mimetype':'application/xml',
                            'index_content':'application',
                            'type':'binary',
                            'datas_fname':(self.xmlname)
                    }
        self.env['ir.attachment'].create(attachment_xml)
        attachment_pdf={
                            'res_id': invoice_br.id,
                            'res_model': 'account.invoice',
                            'name': (self.pdfname),
                            'db_datas': self.pdf,
                            'mimetype':'application/pdf',
                            'index_content':'application',
                            'type':'binary',
                            'datas_fname':(self.pdfname)


                    }
        self.env['ir.attachment'].create(attachment_pdf)
        if self.file_one and self.file_one_name:
            attachment_file={
                                'res_id': invoice_br.id,
                                'res_model': 'account.invoice',
                                'name': (self.file_one_name),
                                'db_datas': self.file_one,
                                'mimetype':'application/pdf',
                                'index_content':'application',
                                'type':'binary',
                                'datas_fname':(self.file_one_name)
                        }
            self.env['ir.attachment'].create(attachment_file)        
        self.write({'modified_by_user':True})
        self.write({'state':'done'})
        return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}

    @api.onchange('invoice_select')
    def _onchange_invoice_select(self):
        invoice = self.env['account.invoice']
        invoice_br = invoice.browse(self.invoice_select)
        invoice_subs_name = 'Factura: ' + '/' \
            + str(invoice_br.reference) + '- ' + 'OC: ' \
            + str(invoice_br.origin) + ' - ' + 'Factura Monto: ' + '/' \
            + str(invoice_br.amount_total)
        self.invoice_select_name = invoice_subs_name

    @api.multi
    def valid(self):
        
        # De la tabla o modelo de esta clase cambiara el valor de estado a confirm
        self.state = 'confirm'
        if self.invoice_select:
            """ Si realiza una búsqueda predeterminada, lo está haciendo con los derechos 
            y privilegios de usuario del usuario actual que ejecuta este comando / acción. 
            Por ejemplo: si no tiene derechos para el modelo "account.invoice" y en su código, 
            self.env ['account.invoice']. Buscar ([]) devolverá una advertencia de seguridad. 
            Si desea omitir esto, puede usar sudo (). Si usa sudo (), Odoo ejecutará su comando 
            como si lo ejecutara un usuario con todos los derechos sobre todo 
            """
            invoice_id = int(self.invoice_select)
            """  El atributo env de cualquier conjunto de registros, disponible como self.env, es un
instancia de la clase Environment definida en el módulo odoo.api. Esta clase juega un
papel central en el desarrollo de Odoo:
Proporciona un acceso directo al registro emulando un diccionario Python; Si
sabes el nombre del modelo que estás buscando, self.env [model_name]
obtendrá un conjunto de registros vacío para ese modelo. Además, el conjunto de registros será
compartir el ambiente de uno mismo.
Tiene un atributo cr que es un cursor de base de datos que puede usar para pasar una consulta SQL sin procesar.
"""            
            self.env.cr.execute("update  public.account_invoice set  state = 'open' where account_invoice.id="+str(invoice_id)+";")
        return True

    @api.multi
    def draft(self):
        self.state = 'draft'
        return True

#58877216/Abca1373