# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class cxp_proveedoresdcp(models.Model):

    _name = 'cuentas_por_pagar.complemento_de_pago_proveedor.model'
    _description = 'CXP Complemento de pago Proveedores'
    _rec_name ='invoice_select_name_cdp'

    

    @api.model
    def _get_partner(self):
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        return user_br.partner_id.id

    @api.model
    def _get_custom(self):
        return self._uid
       
    @api.one
    def _get_self_invoice(self):
        invoice = self.env['account.payment']
        
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        rfc = user_br.partner_id.vat
        partner = self.env['res.partner']
        partner_ids = partner.search([('vat', 'ilike', rfc)])
        partner_ids = [x.id for x in partner_ids]              
        invoice_ids = invoice.search([('partner_id', '=',
                                           tuple(partner_ids)), ('partner_type', '=', 'supplier'),
                                          ('state', 'in', ('posted', )),('state_files', 'in', ('pending', ))]).ids
        print(invoice_ids)
        return ['id','in',invoice_ids]                                          

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
        obj = self.env['cuentas_por_pagar.complemento_de_pago_proveedor.model'].search([('partner_id', '=', partner_ids)]).ids        
        return [('id', 'in', obj)]


    search_ids = fields.Char(
        compute="_compute_search_ids", search='search_ids_search1')

    #search_self_invoice=fields.Char(search='_get_self_invoice')
    custom_uid=fields.Integer(compute="_get_custom")
    partner_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        readonly=True,
        change_default=True,
        track_visibility='always',
        default=_get_partner,
    )
    
    rfc = fields.Char('RFC', related='partner_id.vat', readonly=True,
                      size=13)
    phone = fields.Char('Telefono', related='partner_id.phone',
                        readonly=True)
    email = fields.Char(string='Correo', related='partner_id.email',
                        readonly=True)
    
    STATES = [('draft', 'Borrador'), ('done', 'Finalizado')]
    state = fields.Selection(STATES, default=STATES[0][0])

    fechafactura_xcp_cdp = fields.Datetime(
        'Fecha:',
        required=True,
        index=True,
        readonly=True,
        copy=False,
        default=fields.Datetime.now,
        help='Representa la fecha en la que se crea el archivo.',
    )

    xml_cxp_cdp = fields.Binary(
        string='Archivo Xml', required=True)
    xmlname_cxp_cdp = fields.Char()

    pdf_cxp_cdp = fields.Binary(
        string='Archivo PDF', required=True)
    pdfname_cxp_cdp = fields.Char()
    modified_by_user=fields.Boolean(default=False)


    invoice_select_cdp = fields.Selection('_get_reference_invoice',
                                      string='Referencia del complemento de pago', store=True,required=True)

    invoice_select_name_cdp = fields.Char('Referencia del complemento de pago')
    
    @api.one
    @api.constrains('xmlname_cxp_cdp')
    def _check_xmlname(self):
        if not self.xmlname_cxp_cdp:
            raise UserError(_('No hay Archivo'))
        else:
            tmp = self.xmlname_cxp_cdp.endswith('.xml')
            if tmp is False:
                raise UserError(_('El archivo debe ser XML'))
        
    @api.one
    @api.constrains('pdfname_cxp_cdp')
    def _check_pdfname(self):
        if not self.pdfname_cxp_cdp:
            raise UserError(_('No hay Archivo'))
        if not self.invoice_select_cdp:
            raise UserError(_('Favor de ligar con la referencia del complemento'))
        else:
            tmp = self.pdfname_cxp_cdp.endswith('.pdf')
            if tmp is False:
                raise UserError(_('El archivo debe ser PDF'))
        self.modified_by_user=True
        account_invoice = self.env['account.payment']        
        account_invoice_data=account_invoice.search([('id','=',self.invoice_select_cdp)])
        print(account_invoice_data.state_files)
        print(type(account_invoice_data.state_files))
        account_invoice_data.write({'state_files':'uploaded'})
        self.write({'state':'done'})
        attachment_xml={
                            'res_id': account_invoice_data.id,
                            'res_model': 'account.payment',
                            'name': (self.xmlname_cxp_cdp),
                            'db_datas': self.xml_cxp_cdp,
                            'mimetype':'application/xml',
                            'index_content':'application',
                            'type':'binary',
                            'datas_fname':(self.xmlname_cxp_cdp)
                    }
        self.env['ir.attachment'].create(attachment_xml)
        attachment_pdf={
                            'res_id': account_invoice_data.id,
                            'res_model': 'account.payment',
                            'name': (self.pdfname_cxp_cdp),
                            'db_datas': self.pdf_cxp_cdp,
                            'mimetype':'application/pdf',
                            'index_content':'application',
                            'type':'binary',
                            'datas_fname':(self.pdfname_cxp_cdp)        
                    }
        self.env['ir.attachment'].create(attachment_pdf)
        return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}

                
    _order = 'state desc'

    _defaults = {'state': 'draft',
                 'fechafactura_xcp_cdp': fields.Date.today()}


##################Errr
    @api.model
    def _get_reference_invoice(self):
        invoice = self.env['account.payment']
        
        user = self._uid
        user_br = self.env['res.users'].browse(user)
        rfc = user_br.partner_id.vat
        partner = self.env['res.partner']
        partner_ids = partner.search([('vat', 'ilike', rfc)])
        partner_ids = [x.id for x in partner_ids]

        if user != 1:        
            invoice_ids = invoice.search([('partner_id', 'in', tuple(partner_ids)), ('partner_type', '=', 'supplier'), ('communication', 'not ilike', 'Benef'),
                                          ('communication',
                                           'not ilike', 'depuracion'),
                                          ('communication', 'not ilike', 'saldo'), ('state', 'in', ['reconciled', 'posted']), ('state_files', 'in', ['pending'])])
        else:
            invoice_ids = invoice.search([('partner_type', '=', 'supplier'),
                                          ('state', 'in', ('posted', )),('state_files', 'in', ('pending', ))])       
        selection = []
        if invoice_ids:
            for inv in invoice_ids:
                invoice_subs_name = 'Concepto:\t' + str(inv.communication) \
                    + '  ' + 'Cantidad:\t' + str(inv.amount) 
                xval = (inv.id, invoice_subs_name)
                selection.append(xval)
        return selection


    @api.onchange('invoice_select_cdp')
    def _onchange_invoice_select(self):
        invoice = self.env['account.payment']
        invoice_br = invoice.browse(self.invoice_select_cdp)
        invoice_subs_name = 'Concepto:' + str(invoice_br.communication) \
                    + '  ' + 'Cantidad:' + str(invoice_br.amount) 
        self.invoice_select_name_cdp = invoice_subs_name
