# -*- coding: utf-8 -*-


from odoo import models, fields, api
from ..scripts.sql_server import Get_Axtrax_Attendandce
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime,timedelta
import pytz
from odoo.exceptions import UserError,ValidationError
import math
from odoo.tools.float_utils import float_compare, float_round

class Mayordomia(models.Model):
    _name = 'hr_payroll_pr.mayordomia'
    _description = 'Mayordomia'
    _rec_name = 'record_name'
    fecha = fields.Date()
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho'),('blocked', 'Bloqueado'),('cancel', 'Cancelado')], string='Estado', default='draft')
    mayordomia_lines = fields.One2many('hr_payroll_pr.mayordomia_line', 'mayordomia_id',ondelete='cascade')
    active = fields.Boolean(default=True)
    empleados_con_horas_count = fields.Integer(compute='_compute_empleados_con_horas', string='Empleados Con Horas Registradas')
    empleados_sin_horas_count = fields.Integer(compute='_compute_empleados_sin_horas', string='Empleados Sin Horas Registradas')
    empleados_sin_proyecto_count = fields.Integer(compute='_compute_empleados_sin_proyecto', string='Empleados Sin Proyecto')
    empleados_con_proyecto_count = fields.Integer(compute='_compute_empleados_con_proyecto', string='Empleados Con Proyecto')
    revisados_count = fields.Char(compute='_compute_revisados_count')
    no_revisados_count = fields.Char(compute='_compute_no_revisados_count')
    incidencias_count = fields.Char(compute='_compute_incidencias_count')
    incidencias_validadas_count = fields.Char(compute='_compute_incidencias_validadas_count')
    incidencias_no_validadas_count = fields.Char(compute='_compute_incidencias_no_validadas_count')
    registros_count = fields.Char(compute='_compute_registros_count')
    record_name = fields.Char(compute='_compute_name',string='Fecha y Día')

    @api.multi
    def compute_row(self):
        for record in self:
            for line in record.mayordomia_lines:
                line.compute_bonos()

    

    

    def _compute_registros_count(self):
        self.registros_count = len(self.mayordomia_lines.search([('mayordomia_id','in',[self.id])]))

    @api.multi
    def get_todos_los_registros(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Todos Los Registros',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id', 'in',self.mayordomia_lines.search([('mayordomia_id','in',[self.id])]).ids)]
        }        

    @api.multi
    def get_incidencias_validadas(self):
        pass
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incidencias Validadas',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id', 'in',self.ids)]
        }

    def _compute_incidencias_count(self):
        self.incidencias_count = len(self.mayordomia_lines.mapped('incidencia_ids').ids)
        

    def _compute_incidencias_validadas_count(self):
        self.incidencias_validadas_count = self.mayordomia_lines.mapped('incidencia_ids').mapped('state').count('done')

    def _compute_incidencias_no_validadas_count(self):
        self.incidencias_no_validadas_count = self.mayordomia_lines.mapped('incidencia_ids').mapped('state').count('draft')

    @api.multi
    def get_incidencias_validadas(self):
        ids =[]
        incidencias = self.incidencias_validadas_count = self.mayordomia_lines.mapped('incidencia_ids')
        for incidencia in incidencias:
            if incidencia.state=='done':
                ids.append(incidencia.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incidencias Validadas',
            'view_mode': 'tree,form',
            'res_model': 'hr_4g_payroll_ext.incidency',
            'target': 'current',
            'domain': [('id', 'in',ids)]
        }

    @api.multi
    def get_incidencias_no_validadas(self):
        ids =[]
        incidencias = self.incidencias_validadas_count = self.mayordomia_lines.mapped('incidencia_ids')
        for incidencia in incidencias:
            if incidencia.state=='draft':
                ids.append(incidencia.id)               
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incidencias por Validar',
            'view_mode': 'tree,form',
            'res_model': 'hr_4g_payroll_ext.incidency',
            'target': 'current',
            'domain': [('id', 'in',ids)]
        }

    @api.multi
    def get_incidencias(self):
        incidencias = self.incidencias_validadas_count = self.mayordomia_lines.mapped('incidencia_ids')               
        return {
            'type': 'ir.actions.act_window',
            'name': 'Todas las Incidencias',
            'view_mode': 'tree,form',
            'res_model': 'hr_4g_payroll_ext.incidency',
            'target': 'current',
            'domain': [('id', 'in',incidencias.ids)]
        }
    def _compute_empleados_con_horas(self):
        count = []
        for record in self.mayordomia_lines:
            if (sum(record.horas_proyecto_ids.mapped('horas')) >0):
                count.append(record.id)  
        self.empleados_con_horas_count=len(count)

    def _compute_empleados_sin_horas(self):
        count = []
        for record in self.mayordomia_lines:
            if ((not record.horas_proyecto_ids) or (sum(record.horas_proyecto_ids.mapped('horas'))<=0)):
                count.append(record.id)  
        self.empleados_sin_horas_count=len(count)

    def _compute_empleados_sin_proyecto(self):
        count = []
        for record in self.mayordomia_lines:
            if (not record.horas_proyecto_ids):
                count.append(record.id)
        self.empleados_sin_proyecto_count=len(count)

    @api.one
    def _compute_empleados_con_proyecto(self):
        count = []
        for record in self.mayordomia_lines:
            if record.horas_proyecto_ids:
                count.append(record.id)
        self.empleados_con_proyecto_count=len(count)
        
            


    def _compute_no_revisados_count(self):        
        self.no_revisados_count = len(self.mayordomia_lines.search([('id','in',self.mayordomia_lines.ids),'|',('revision','in',['draft']),('revision','in',[False])]).ids)

    def _compute_revisados_count(self):
        self.revisados_count = len(self.mayordomia_lines.search([('revision','in',['done']),('id','in',self.mayordomia_lines.ids)]).ids)
    
    @api.multi
    def get_revisados(self):       
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incidencias Validadas',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id', 'in',self.mayordomia_lines.search([('revision','in',['done']),('id','in',self.mayordomia_lines.ids)]).ids)]
        }

    @api.multi
    def get_con_proyecto(self):
        count = []
        for record in self.mayordomia_lines:
            if record.horas_proyecto_ids:
                count.append(record.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Con Proyecto',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id','in',count)]
        }

    @api.multi
    def get_empleados_con_horas(self):  
        count = []
        for record in self.mayordomia_lines:
            if (sum(record.horas_proyecto_ids.mapped('horas')) >0):
                count.append(record.id)     
        return {
            'type': 'ir.actions.act_window',
            'name': 'Empleados con Horas de Proyecto',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id', 'in',count)]
        }
    @api.multi
    def get_empleados_sin_horas(self):   
        count = []
        for record in self.mayordomia_lines:
            if (sum(record.horas_proyecto_ids.mapped('horas'))<=0):
                count.append(record.id) 
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sin Horas de Proyecto',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id', 'in',count)]
        }
    @api.multi
    def get_sin_proyecto(self):   
        count = []
        for record in self.mayordomia_lines:
            if not(record.horas_proyecto_ids):
                count.append(record.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sin Proyecto',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id','in',count)]
        }

    def set_compute_incidencias_count(self):
        self.mayordomia_lines.compute_incidencias_count()

    @api.multi
    def get_no_revisados(self):   
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mayordomías No Revisadas',
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.mayordomia_line',
            'target': 'current',
            'domain': [('id', 'in',self.mayordomia_lines.search([('revision','in',['draft']),('id','in',self.mayordomia_lines.ids)]).ids)]
        }


    @api.model
    def create(self, vals):        
        hr_contract = self.env['hr.contract']
        employees = hr_contract.search([('employee_id', '!=', False), ('state', 'in', ['open'])])
        new_recs = []
        for employee in employees:
            
            new_recs.append(
                [0, 0, {'revision': 'draft', 'departamento': employee.employee_id.department_id.id, 'operador': employee.employee_id.id, 'bonos_ids': [[6, False, []]]}]
                )        
        vals['mayordomia_lines']=new_recs
        self_ctx = self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)
        return super(Mayordomia, self_ctx).create(vals)

    @api.multi
    def create_mult(self,vals):
        recs = self.env[self.mayordomia_lines._name].with_context(mail_create_nolog=True, mail_create_nosubscribe=True).create(vals)
        return recs

    @api.one
    def cerrar_dia(self):
        # if not (int(self.no_revisados_count) ==0):
        #     raise ValidationError('Ups!!!!\n:(\n Asegurese de que todos los registros se encuentren  en estatus "Revisado"')
        # if not (self.incidencias_validadas_count==self.incidencias_count):
        #     raise ValidationError('Ups!!!!\n:(\n Asegurese de que todas las incidencias se encuentren Validadas')
        self.state = 'done'

    @api.one
    def bloquear_dia(self):
        self.state = 'blocked'

    @api.one
    def des_bloquear_dia(self):
        self.state = 'draft'

    @api.one
    def check_close(self):
        if self.state =='blocked':
            raise ValidationError('Ups!!!!\n:(\n La Mayordomía de este día se encuentra Bloqueada, no se pueden agregar más incidencias.')


    @api.one
    def bloquear_dia(self):
        self.state = 'blocked'

    @api.one
    def desbloquear_dia(self):
        self.state = 'draft'
        
    @api.multi
    def calcular_mayordomia(self):
        self.mayordomia_lines.compute_horas_a_pagar()
        self.mayordomia_lines.compute_bonos()
        self.mayordomia_lines.compute_revision()

#Cambiar a modelo mayordomia
    @api.multi
    def get_horas_checador(self):
        unlink_ids=[]
        for item in self.mayordomia_lines:
            if item.operador.id == 337:
                print('Error')            
            unlink_ids.extend(item.entradas_salidas.ids)
            numero_de_dia=item.operador.turno.dia_de_la_semana(item.mayordomia_id.fecha)      
            turno_line=item.operador.turno.turno_line_ids.filtered(lambda x: x.turno_id.id ==item.operador.turno.id and x.dia==numero_de_dia[0])            
            # turno_line2=item.operador.turno.turno_line_ids.search([('turno_id','in',[item.operador.turno.id]),('dia','in',numero_de_dia)])
            delta=timedelta(days=0)
            if turno_line.between_days:
                delta = timedelta(minutes=30,days=1)
            else:
                delta= timedelta(minutes=30)
            entrada = item.mayordomia_id.fecha+self.float_to_time_str(turno_line.hour_from)
            salida = item.mayordomia_id.fecha+self.float_to_time_str(turno_line.hour_to)
            entrada_dt =datetime.strptime(entrada, DEFAULT_SERVER_DATETIME_FORMAT)-timedelta(minutes=30)
            salida_dt =datetime.strptime(salida, DEFAULT_SERVER_DATETIME_FORMAT)+delta
            entrada = datetime.strftime(entrada_dt,DEFAULT_SERVER_DATETIME_FORMAT)
            salida = datetime.strftime(salida_dt,DEFAULT_SERVER_DATETIME_FORMAT)
            try:                
                horas_checador = Get_Axtrax_Attendandce(item.operador.idaxtraxng,entrada,salida)
                if len(horas_checador)==2:                    
                       item.entradas_salidas.create({'mayordomia_line_id':item.id,'date_in': self.local_to_utc(horas_checador[0]), 'date_out': self.local_to_utc(horas_checador[1])})
            except Exception as e:
                print(e)                                                        
        self.env['hr_payroll_pr.in_out'].search([('id','in',unlink_ids)]).unlink()
        
    


    def float_to_time_str(self,float_time):
        return ' {0:02.0f}:{1:02.0f}:00'.format(*divmod(float(float_time) * 60, 60))

    def local_to_utc(self,date):
        local = pytz.timezone("America/Mexico_City")
        naive = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt


    @api.multi
    def _compute_name(self):      
        for record in self:   
            fecha = record.fecha
            dia = record.dia_de_la_semana_nombre(record.fecha)[0]
            record.record_name = "%s %s" % (dia,fecha)
        return

    @api.multi
    def name_get(self):
        res = []        
        for record in self:   
            fecha = record.fecha
            dia = record.dia_de_la_semana_nombre(record.fecha)[0]
            # res.append((record.id,("%s %s" % (dia,fecha[:10]))))
            res.append((record.id,("%s %s" % (dia,fecha))))
        return res

    @api.one
    def dia_de_la_semana(self,date):
        try:
             return str(datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT).weekday())
        except:
            pass

    @api.one
    def dia_de_la_semana_nombre(self,date):
        dia = self.dia_de_la_semana(date)[0]
        if dia in ['0']:
            return 'Lunes'
        if dia in ['1']:
            return 'Martes'
        if dia in ['2']:
            return 'Miércoles'
        if dia in ['3']:
            return 'Jueves'
        if dia in ['4']:
            return 'Viernes'
        if dia in ['5']:
            'Sábado'
        if dia in ['6']:
            return 'Domingo'

    @api.one
    def utc_to_local_to_str(self,date):
        local = pytz.timezone(self.env.user.tz or pytz.utc)
        return datetime.strftime(pytz.utc.localize(datetime.strptime(date,DEFAULT_SERVER_DATE_FORMAT)).astimezone(local),DEFAULT_SERVER_DATETIME_FORMAT)


    @api.model
    def search_read(self, domain=None, fields=None, offset=0,limit=None, order=None):        
        res = super(Mayordomia, self).search_read(domain, fields, offset, limit, order)
        return res
    

    @api.multi
    def write(self, values):
        # Add code here
        return super(Mayordomia, self).write(values)
    