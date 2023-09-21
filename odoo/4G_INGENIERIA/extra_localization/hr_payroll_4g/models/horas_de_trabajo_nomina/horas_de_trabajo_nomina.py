# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime   
import pytz

class horas_de_trabajo_nomina(models.Model):
    _name = 'hr_payroll_4g.horas_de_trabajo_nomina'
    _rec_name = 'operador'

    #El operador tiene id_axtrax
    departamento = fields.Many2one('hr.department')
    operador = fields.Many2one('hr.employee')



    horas_de_trabajo_nomina_ids = fields.Many2one(
        'hr_payroll_4g.detalle_horas_de_trabajo_nomina',ondelete='cascade')



    horas_mayordomia = fields.Float()
    horas_checador = fields.Float()
    horas_a_pagar = fields.Float()
    bono_de_asistencia = fields.Boolean()
    bono_de_puntualidad = fields.Boolean()
    balance_de_horas = fields.Float('Balance de Horas')

    nota=fields.Char()
    incidencia_id_holidays = fields.Many2one('hr.holidays')
    estado_incidencia = fields.Selection(string='Estado de Incidencia',related='incidencia_id_holidays.state')
    entrada_salida = fields.Html()
    read_only = fields.Boolean(default=False)
    valid = fields.Boolean(default=False)

    @api.onchange('horas_mayordomia','horas_checador')
    def _compute_horas_a_pagar(self):
        aux_horas_checador=self.horas_checador
        if aux_horas_checador>10:
            aux_horas_checador=10
        self.update({'horas_mayordomia':self.horas_mayordomia})
        self.update({'horas_checador':self.horas_checador})
        self.update({'horas_a_pagar':aux_horas_checador})
        self.update({'valid':True})
        self.update({'operador':self._origin.operador.id})
        

        if self.horas_mayordomia==0 and self.horas_checador==0 and not self.incidencia_id_holidays:
            balance_de_horas=self.env['hr_payroll_4g.historial_de_tiempo']
            existing_balance_de_horas = balance_de_horas.search(['|',('horas_de_trabajo_nomina_line','in',[self._origin.id]),('horas_de_trabajo_nomina_line','=',False)])
            if existing_balance_de_horas:
                existing_balance_de_horas.unlink()
            self.update({'balance_de_horas':10})
            self.update({'operador':self._origin.operador.id})

            print(existing_balance_de_horas)
            vals_historial_de_tiempo={
                'horas_de_trabajo_nomina_line':self._origin.id,
                    'operador': self._origin.operador.id,
                    'active': True,
                    'horas_en_contra':10,
                    'state': 'to_approve',
                    'tipo_pago': 'undef',
            }
            self.env['hr_payroll_4g.historial_de_tiempo'].create(
                    vals_historial_de_tiempo)
        
        elif self.horas_mayordomia==9.5 and self.horas_checador==10 and not self.incidencia_id_holidays:
            balance_de_horas=self.env['hr_payroll_4g.historial_de_tiempo']
            existing_balance_de_horas = balance_de_horas.search(['|',('horas_de_trabajo_nomina_line','in',[self._origin.id]),('horas_de_trabajo_nomina_line','=',False)])
            if existing_balance_de_horas:
                existing_balance_de_horas.unlink()
            self.update({'balance_de_horas':0})
            self.update({'operador':self._origin.operador.id})  
                

        elif self.horas_mayordomia>9.5 and self.horas_checador >10 and not self.incidencia_id_holidays:
            balance_de_horas=self.env['hr_payroll_4g.historial_de_tiempo']
            existing_balance_de_horas = balance_de_horas.search(['|',('horas_de_trabajo_nomina_line','in',[self._origin.id]),('horas_de_trabajo_nomina_line','=',False)])
            if existing_balance_de_horas:
                existing_balance_de_horas.write({'horas_a_favor':self.horas_checador-10})
                existing_balance_de_horas.write({'horas_en_contra':False})
            if not existing_balance_de_horas:
                balance_de_horas.create({'operador':self.operador.id,'horas_de_trabajo_nomina_line':self._origin.id,
                'state':'to_approve',
                'tipo_pago':'undef',
                'horas_a_favor':self.horas_checador-10})
            self.update({'balance_de_horas':self.horas_checador-10})


        elif self.horas_mayordomia<9.5 and self.horas_mayordomia>0 and self.horas_checador <10 and not self.incidencia_id_holidays:
            balance_de_horas=self.env['hr_payroll_4g.historial_de_tiempo']
            existing_balance_de_horas = balance_de_horas.search(['|',('horas_de_trabajo_nomina_line','in',[self._origin.id]),('horas_de_trabajo_nomina_line','=',False)])
            if existing_balance_de_horas:
                existing_balance_de_horas.write({'horas_a_favor':False})
                existing_balance_de_horas.write({'horas_en_contra':10-self.horas_checador})
            if not existing_balance_de_horas:
                balance_de_horas.create({'operador':self.operador.id,'horas_de_trabajo_nomina_line':self._origin.id,
                'state':'to_approve',
                'tipo_pago':'undef',
                'horas_en_contra':10-self.horas_checador})
            self.update({'balance_de_horas':10-self.horas_checador})

        elif self.horas_mayordomia>=9.5 and self.horas_mayordomia>0 and self.horas_checador <=10 and not self.incidencia_id_holidays:
            balance_de_horas=self.env['hr_payroll_4g.historial_de_tiempo']
            existing_balance_de_horas = balance_de_horas.search(['|',('horas_de_trabajo_nomina_line','in',[self._origin.id]),('horas_de_trabajo_nomina_line','=',False)])
            if existing_balance_de_horas:
                existing_balance_de_horas.unlink()
            self.update({'balance_de_horas':False})
            self.update({'valid':False})

 
        

                



        
        
        


