from odoo import _, api, fields, models
from odoo import tools, _
DEFAULT_NUMERO_CREDITO_INFONAVIT='          '
import datetime
class Employee(models.Model):
    _inherit = 'hr.employee'
    names = fields.Char(string='Nombre(s)')
    first_name = fields.Char(string='Apellido Paterno')
    second_name = fields.Char(string='Apellido Materno')
    unidad_de_medicina_familiar = fields.Char(string='UMF')
    state_sua_idse = fields.Selection(string='Estado de Registro SUA/IDSE',selection=[
            ('normal', 'In Progress'),
            ('blocked', 'Blocked'),
            ('done', 'Ready for next stage')],default='normal')
    # aseg_id = fields.Many2one('sua.aseg', string='Aseg ID')
    aseg_id = fields.Many2many('sua.aseg',string='Alta')
    mov_id = fields.Many2many('sua.mov',string='Baja, Modificación de Salario o Reingreso')
    cred_mov_id = fields.Many2many('sua.mov.cr',string='Movimientos de Crédito')
    incapacidad_id = fields.Many2many('sua.mov.incap',string='Incapacidad')
    idse_id = fields.Many2many('sua.idse',string='Registro IDSE')
    afil_id = fields.Many2many('sua.afil',string='Datos Afiliatorios')
    
    
    @api.model
    def create(self, vals):
        if vals.get('user_id'):
            vals.update(self._sync_user(self.env['res.users'].browse(vals['user_id'])))
        tools.image_resize_images(vals)
        return super(Employee, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'address_home_id' in vals:
            account_id = vals.get('bank_account_id') or self.bank_account_id.id
            if account_id:
                self.env['res.partner.bank'].browse(account_id).partner_id = vals['address_home_id']
        tools.image_resize_images(vals)
        if all(key in vals for key in ("names","first_name","second_name")):            
            complete_name = '%s %s %s' % (vals.get('names').upper().lstrip().rstrip() or self.names.upper().lstrip().rstrip() or '',vals.get('first_name').upper().lstrip().rstrip() or self.first_name.upper().lstrip().rstrip() or '',vals.get('second_name').upper().lstrip().rstrip() or self.second_name.upper().lstrip().rstrip() or '')
            self.contract_id.write({'name':complete_name})  
            vals.update({'name':complete_name})
        res = super(Employee, self).write(vals)
        return res
    
    @api.one
    def create_complete_row(self):
        str_credito_infonavit = DEFAULT_NUMERO_CREDITO_INFONAVIT
        print(len(str(self.cred_infonavit)))
        if (len(str(self.cred_infonavit))==10):
            str_credito_infonavit = str(self.cred_infonavit)
        vals = {
            'registro_patronal_imss':self.company_id.registro_patronal,
            'numero_de_seguridad_social':self.segurosocial,
            'reg_fed_de_contribuyentes':self.rfc,
            'curp':self.curp,
            'nombre':self.names,
            'apellido_paterno':self.first_name,
            'apellido_materno':self.second_name,
            'fecha_de_alta':fields.Datetime.from_string(self.contract_id.date_start).strftime("%d%m%Y"),
            'salario_diario_integrado':"{:.2f}".format((self.contract_id.sueldo_diario_integrado)) ,
            'numero_de_credito_infonavit':str_credito_infonavit,
            'fecha_de_inicio_de_descuento':'00000000', #usar or para la fecha de inicio de descuento
            'tipo_de_descuento': '0',#usar or            
            'clave_de_municipio':self.env.user.company_id.registro_patronal[:3],
            'employee_id':self.id  
        }
        rec = self.env['sua.aseg'].create(vals)
        rec.get_complete_row_aseg()
        self.contract_id.employee_id.aseg_id = [(4,rec.id)]         
        

    @api.one
    def create_complete_row_afil(self):
        estado = self.env['sua.estados'].search([('descripcion', 'ilike',self.address_home_id.state_id.name)])
        if not estado:
            print('error')
        sexo=''
        if self.gender == 'male':
            sexo='M'
        if self.gender == 'female':
            sexo='F'    
        vals = {
            'registro_patronal_imss':self.company_id.registro_patronal,
            'numero_de_seguridad_social':self.segurosocial,
            'codigo_postal':self.address_home_id.zip,
            'fecha_de_nacimiento':datetime.datetime.strptime(self.birthday, '%Y-%m-%d').strftime('%d%m%Y'),
            'lugar_de_nacimiento':estado.id,
            'unidad_de_medicina_familiar': self.unidad_de_medicina_familiar or '043',
            # 'clave_lugar_de_nacimiento':,
            'ocupacion':'EMPLEADO',
            'sexo':sexo,
            'tipo_de_salario':0,
            'hora':'',
        }
        rec = self.env['sua.afil'].create(vals)
        if rec:
            rec.get_complete_row_afil()
            self.contract_id.employee_id.afil_id = [(4,rec.id)]     
        