# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class cuentas_por_pagar_repse(models.Model):
    _description = 'Repse'
    _name = 'cuentas_por_pagar_repse.repse'
    _order = "history_id"
    file1 = fields.Binary("Archivo",required=True)
    file1_name = fields.Char("Nombre",required=True)
    type = fields.Selection(string='Tipo de Documento', selection=[('cfdi','CFDI de nómina de los trabajadores con los que se haya proporcionado el servicio.'), 
                                                                        ('comprobantes', 'Comprobantes de pago (Por la declaración y entero de las retenciones de impuestos realizadas a dichos trabajadores, de cuotas obrero patronales del IMSS y de las aportaciones al INFONAVIT).'),
                                                                        ('registro','Copia de tu registro vigente en el padrón de la STPS (REPSE).'), 
                                                                        ('iva_declaracion','Declaración del IVA correspondiente al periodo en que el contratante (tu cliente) hizo el pago de la contraprestación.'), 
                                                                        ('iva_acuse','Acuse de recibo del pago del IVA correspondiente al periodo en que el contratante (tu cliente) hizo el pago de la contraprestación.')],required=True)
    history_id = fields.Many2one('cuentas_por_pagar_repse.history')
    
    @api.onchange('type','file1')
    def _onchange_type_file(self):
        if self.type:
            self.file1_name=self.type
        else:
            raise UserError(('Por favor, Seleccione un Tipo'))

    


class cuentas_por_pagar_repse_history(models.Model):
    _name = 'cuentas_por_pagar_repse.history'
    _description = 'Repse Historial'
    _order = "partner_id"
    active = fields.Boolean(string='Archivado',default=True,required=True)
    mes = fields.Selection([
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ], string='Mes', required=True)

    ano = fields.Selection([
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
    ], string='Año', required=True)

    state = fields.Selection(selection=[('done', 'Verificado'), ('draft', 'Pendiente')],default='draft')
    repse_lines = fields.One2many('cuentas_por_pagar_repse.repse','history_id')
    _rec_name = 'get_rec_name'

    get_rec_name = fields.Char(compute='rec_name')
    partner_id = fields.Many2one('res.partner',string="Nombre",default=lambda self: self.env.user.partner_id.parent_id.id)
    
    def action_valid(self):
        if self.partner_id.aplica_repse=='yes':
            self.partner_id.estado_repse='done'
            self.state='done'
        else:
            raise UserError(('El provedor No tiene habilitado REPSE'))


    def action_draft(self):
        self.partner_id.estado_repse='draft'
        self.state='draft'

    @api.model
    def create(self, values):
        # CODE HERE
        return super(cuentas_por_pagar_repse_history, self).create(values)

    @api.multi
    def write(self, values):
        res = super(cuentas_por_pagar_repse_history, self).write(values)
        # here you can do accordingly
        return res

    @api.multi
    def unlink(self):
        # CODE HERE
        self.action_draft()
        return super(cuentas_por_pagar_repse_history, self).unlink()

    @api.constrains('repse_lines')
    def documentos_completos(self):
        if len(self.repse_lines.ids) <6:            
            cfdi_count=self.env['cuentas_por_pagar_repse.repse'].search_count([('id', 'in',self.repse_lines.ids),('type','=','cfdi')])
            comprobantes_count=self.env['cuentas_por_pagar_repse.repse'].search_count([('id', 'in',self.repse_lines.ids),('type','=','comprobantes')])
            registro_count=self.env['cuentas_por_pagar_repse.repse'].search_count([('id', 'in',self.repse_lines.ids),('type','=','registro')])
            iva_declaracion_count=self.env['cuentas_por_pagar_repse.repse'].search_count([('id', 'in',self.repse_lines.ids),('type','=','iva_declaracion')])
            iva_acuse_count=self.env['cuentas_por_pagar_repse.repse'].search_count([('id', 'in',self.repse_lines.ids),('type','=','iva_acuse')])
            if cfdi_count>1 or comprobantes_count >1 or registro_count>1 or iva_declaracion_count >1 or iva_acuse_count>1:
                raise UserError(('Solo puede existir un tipo de documento por mes, asegurese que no esté intentando subir un tipo de documento que ya existe.'))
        else:
            raise UserError(('Solo se pueden subir los 5 archivos del tipo requerido.'))



    def rec_name(self):
        for test in self:
            test.get_rec_name= test.mes+" "+test.ano+" "+self.state

    def return_views(self):
        if self.env['res.users'].has_group('cuentas_por_pagar_repse.group_cuentas_por_pagar_admin'):
            partner_ids = self.env['res.partner'].search([('active','=',True),('is_company', '=', True)]).ids
            return{
                'name': 'Documentos REPSE',
                'view_type': 'form',
                "view_mode": "pivot",
                "view_mode": "tree,form",
                'view_id': False,
                "res_model": "cuentas_por_pagar_repse.history",
                #'views': views,
                'domain': [('partner_id','in',partner_ids)],
                'type': 'ir.actions.act_window',
            }
        user = self.env.user.id
        user_br = self.env['res.users'].browse(user)
        rfc = user_br.partner_id.vat
        if not rfc:
            raise UserError(('El Usuario no tiene RFC configurado.'))
        partner = self.env['res.partner']        
        if self.env.user.partner_id.parent_id.id:
            partner_ids = partner.browse(self.env.user.partner_id.parent_id.id)
        elif self.env.user.partner_id.id:
            partner_ids = partner.browse(self.env.user.partner_id.id)
        return{
                'name': 'Mis documentos REPSE',
                'view_type': 'form',
                "view_mode": "pivot",
                "view_mode": "tree,form",
                'view_id': False,
                "res_model": "cuentas_por_pagar_repse.history",
                #'views': views,
                'domain': [('partner_id', 'in', partner_ids.ids)],
                'type': 'ir.actions.act_window',
            }
        



    @api.model
    def create(self, values):
        # CODE HERE        
        count=self.search_count([('mes','in',[values['mes']]),('ano','in',[values['ano']]),('partner_id','in',[self.env.user.partner_id.parent_id.id])])
        if count>0:
            raise UserError(('Ya existe el mes.\t'+values['mes']+'\tdel año\t'+values['ano']))
        return super(cuentas_por_pagar_repse_history, self).create(values)

