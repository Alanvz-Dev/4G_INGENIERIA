# -*- coding: utf-8 -*-

import operator
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime,timedelta
import pytz

class horas_de_trabajo(models.Model):
    _name = 'hr_payroll_pr.mayordomia_line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'operador'
    # _order = "revision asc,total_de_horas asc"
    departamento = fields.Many2one('hr.department')
    operador = fields.Many2one('hr.employee')
    mayordomia_id = fields.Many2one('hr_payroll_pr.mayordomia',ondelete='cascade')    
    horas_proyecto_ids = fields.One2many('hr_payroll_pr.horas_proyecto','mayordomia_line_id',ondelete='cascade')          
    bonos_ids = fields.Many2many('hr_payroll_pr.bonos',track_visibility='onchange')    
    state = fields.Selection(
        string='Estado',
        selection=[('draft', 'Abierto'), ('done', 'Cerrado')],track_visibility='onchange'
    )
    # administrativo = fields.Boolean(related='operador.is_administrativo',string='Administrativo')    
    total_de_horas = fields.Float(compute='get_total_de_horas', digits=(12, 2), store=True)
    incidencia_ids = fields.Many2many('hr_4g_payroll_ext.incidency', compute='_compute_incidencia_ids')
    horas_a_pagar = fields.Float(track_visibility='onchange') 
    entradas_salidas = fields.One2many('hr_payroll_pr.in_out','mayordomia_line_id',ondelete='cascade')
    revision = fields.Selection(
        string='Revision',
        selection=[('done', 'Revisado'), ('draft','Por Revisar')],track_visibility='onchange',
         default='draft'
    )  
    part_ids = fields.Many2many('res.partner')

    incidencias_count = fields.Integer(string='Cant. Incidencias')
    

    def compute_incidencias_count(self):
        for record in self:
            print(len(record.incidencia_ids.ids))
            record.incidencias_count=len(record.incidencia_ids.ids)

    def get_horas_checador(self):
        x = self.env

    @api.multi
    def compute_bonos(self):
        inc_bonos_config=self.env['hr_payroll_pr.incidencias_bonos_configuracion']
        for record in self.web_progress_iter(self, msg="Calculando Bonos"):
            if not (record.revision == 'done'):
                new_recs=[]
                if record.operador.is_administrativo:
                    new_recs.append(record.bonos_ids.search([('codigo','in',['ADMIN'])]).id)  
                    if (record.operador.is_administrativo) and (not record.incidencia_ids):
                        new_recs.append(record.bonos_ids.search([('codigo','in',['P'])]).id)
                        new_recs.append(record.bonos_ids.search([('codigo','in',['A'])]).id)
                        record.bonos_ids = [(6,0,new_recs)]
                        # return record
                        continue                    
                for incidencia in record.incidencia_ids:
                    res  = inc_bonos_config.search([('incidencia_id.codigo','in',[incidencia.tipo_incidencia])],limit=1)
                    if res:
                        if res.puntualidad:
                            new_recs.append(record.bonos_ids.search([('codigo','in',['P'])]).id)
                        if res.asistencia:
                            new_recs.append(record.bonos_ids.search([('codigo','in',['A'])]).id)
                    if new_recs:
                        record.bonos_ids = [(6,0,new_recs)]
                if not record.incidencia_ids:
                    if record.entradas_salidas:
                        if record.entradas_salidas.total>=0:
                            new_recs.append(record.bonos_ids.search([('codigo','in',['A'])]).id)
                        if record.entradas_salidas.bono_puntualidad:
                            new_recs.append(record.bonos_ids.search([('codigo','in',['P'])]).id)
                    if new_recs:
                        record.bonos_ids = [(6,0,new_recs)]

        
    @api.constrains('total_de_horas')
    def _check_total_de_horas(self):
        for record in self:            
            if record.total_de_horas>9.5:
                raise ValidationError('El máximo de horas por día es 9.5, si necesita pagar más de 9.5 horas agregue una incidencia de Tiempo Extra\ny/o \nOrdene por total de horas para determinar el error.')


    @api.multi
    def set_proyecto(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asignar Proyecto(s)',
            'view_mode': 'form',
            'res_model': 'hr_payroll_pr.asign_proyecto',
            'target': 'new',
            'context':{'default_mayordomia_line_ids': [(6,0,self.ids)]}
        }


    @api.multi
    def set_horas_a_pagar(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asignar Hora(s) a Pagar',
            'view_mode': 'form',
            'res_model': 'hr_payroll_pr.asign_horasp',
            'target': 'new',
            'context':{'default_mayordomia_line_ids': [(6,0,self.ids)]}
        }    

    @api.multi
    def compute_revision(self):        
        count=0
        for record in self.web_progress_iter(self, msg="Realizando la revisión"):
            horas_a_pagar_por_turno=record.operador.turno.horas_por_dia
            if not (record.revision == 'done'):
                count=count+1
                print(count)
                incidencias = record.one_compute_incidencia_ids()
                if record.total_de_horas == 9.5 and (not incidencias) and (record.entradas_salidas.total==horas_a_pagar_por_turno) and (record.entradas_salidas.bono_puntualidad):
                    record.revision = 'done'
                elif (not incidencias) and self.is_administrativo_opt(record.operador.id):
                    record.revision = 'done'


    @api.depends('horas_proyecto_ids')
    def get_total_de_horas(self):
        for item in self:
            item.total_de_horas = sum(item.horas_proyecto_ids.mapped('horas'))


    @api.one    
    def _compute_incidencia_ids(self):
        date_from  =self.local_to_utc("%s 00:00:00"%(self.mayordomia_id.fecha)) 
        date_to  =self.local_to_utc("%s 23:59:53"%(self.mayordomia_id.fecha))
        incidency = self.env['hr_4g_payroll_ext.incidency']
        incidencia = incidency.search([('employee_id', 'in', self.operador.ids), (
            'date_from', '>=', date_from), ('date_to', '<=', date_to)])                
        self.incidencia_ids = [(6,0, incidencia.ids)]


    def one_compute_incidencia_ids(rec):
        rec.ensure_one()
        date_from  =rec.local_to_utc("%s 00:00:00"%(rec.mayordomia_id.fecha)) 
        date_to  =rec.local_to_utc("%s 23:59:53"%(rec.mayordomia_id.fecha))        
        incidency = rec.env['hr_4g_payroll_ext.incidency']
        incidencia = incidency.search([('employee_id', 'in', rec.operador.ids), (
            'date_from', '>=',date_from), ('date_to', '<=',date_to)])                
        return incidencia


    @api.multi
    def set_revisado(self):
        for item in self:
            item.revision='done'

    @api.multi
    def set_no_revisado(self):
        for item in self:
            item.revision='draft'


    def is_administrativo_opt(self,employee_id):
        query = 'select is_administrativo  from hr_employee where id = %s'%(employee_id)
        self.env.cr.execute(query)
        return self.env.cr.fetchone()[0]

    def turno_horas_por_dia_opt(self,employee_id):
        query = 'select is_administrativo  from hr_employee where id = %s'%(employee_id)
        self.env.cr.execute(query)
        return self.env.cr.fetchone()[0]


#TODO FIX DO MULTI
    @api.multi
    def compute_horas_a_pagar(self):
        
        inc_bonos_config=self.env['hr_payroll_pr.incidencias_bonos_configuracion']
        count =0
        for item in self.web_progress_iter(self, msg="Calculando Horas a Pagar"):  
            if not item.operador.turno:
                raise ValidationError("Upss!!! El empleado %s necesita tener un turno configurado"%(item.operador.name))
            horas_a_pagar_por_turno=item.operador.turno.horas_por_dia
            if item.revision not in 'done':
                incidencia =item.one_compute_incidencia_ids()
                count=count+1
                if  not incidencia:
                    if self.is_administrativo_opt(item.operador.id):
                            item.horas_a_pagar=horas_a_pagar_por_turno+item.operador.turno.suma_horas
                            continue
                #TODO FIX PERFORMANCE
                
                total=item.entradas_salidas.total
                if item.total_de_horas == 9.5 and (total>=(item.operador.turno.horas_por_dia-0.9)) and item.entradas_salidas.bono_puntualidad:
                    item.horas_a_pagar=horas_a_pagar_por_turno+item.operador.turno.suma_horas
                else:
                    if item.total_de_horas and total:
                        if  total<0:
                            item.horas_a_pagar=0
                        else:
                            item.horas_a_pagar=total
                    if incidencia:
                        for rec_incidencia in incidencia:
                            res  = inc_bonos_config.search([('incidencia_id.codigo','in',[rec_incidencia.tipo_incidencia])],limit=1)
                            if res.diferencia_de_horas:
                                if rec_incidencia.tipo=='min':
                                    item.horas_a_pagar=total+abs(rec_incidencia.horas)
                                    if item.horas_a_pagar>horas_a_pagar_por_turno:
                                        item.horas_a_pagar=horas_a_pagar_por_turno+item.operador.turno.suma_horas
                                if rec_incidencia.tipo=='sum':
                                    item.horas_a_pagar=total-abs(rec_incidencia.horas)
                                    if item.horas_a_pagar<0:
                                        item.horas_a_pagar=0                                    
                            if res.informativo:
                                # return
                                pass
                    else:
                        item.horas_a_pagar=total
                if item.horas_a_pagar<0:
                    item.horas_a_pagar=0
 



    @api.multi
    def ver_incidencias(self):
        return {
            'type': 'ir.actions.act_window',
            'name': ('Incidencia(s) de %s'%self.operador.name),
            'view_mode': 'tree,form',
            'res_model': 'hr_4g_payroll_ext.incidency',
            'target': 'current',
            'domain': [('id', 'in',self.incidencia_ids.ids)]
        }

    @api.multi
    def ver_entradas_y_salidas(self):
        return {
            'type': 'ir.actions.act_window',
            'name': ('Entradas y Salida de %s'%self.operador.name),
            'view_mode': 'tree,form',
            'res_model': 'hr_payroll_pr.in_out',
            'target': 'current',
            'domain': [('id', 'in',self.entradas_salidas.ids)]
        }

    
    @api.multi
    def name_get(self):
        res = []
        for rec in self:                                 
                res.append((rec.id, _("%s Hora(s) a Pagar: %.2f " ) % (rec.mayordomia_id.fecha,rec.horas_a_pagar)))
        return res

    @api.one
    def compute_record(self):
        self.compute_horas_a_pagar()  
        self.compute_bonos()         
        

    def local_to_utc(self,date):
        try:
            local = pytz.timezone("America/Mexico_City")
            naive = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
            local_dt = local.localize(naive, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
        except:
            return
        return datetime.strftime(utc_dt,DEFAULT_SERVER_DATETIME_FORMAT)