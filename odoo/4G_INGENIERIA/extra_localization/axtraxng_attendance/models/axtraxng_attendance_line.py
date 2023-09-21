# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import random



class axtraxng_attendance_line(models.Model):
    _name = 'hr.axtraxng_attendance_line'
    _rec_name = 'employee_id'
    axtraxng_attendance_ids = fields.Many2one('hr.axtraxng_attendance')
    employee_id = fields.Many2one('hr.employee')
    day1_name=fields.Char()
    day2_name=fields.Char()
    day3_name=fields.Char()
    day4_name=fields.Char()
    day5_name=fields.Char()
    day6_name=fields.Char()
    day7_name=fields.Char()
    day1_in=fields.Char()
    day2_in=fields.Char()
    day3_in=fields.Char()
    day4_in=fields.Char()
    day5_in=fields.Char()
    day6_in=fields.Char()
    day7_in=fields.Char()
    day1_out=fields.Char()
    day2_out=fields.Char()
    day3_out=fields.Char()
    day4_out=fields.Char()
    day5_out=fields.Char()
    day6_out=fields.Char()
    day7_out=fields.Char()
    day1_effective_time=fields.Char()
    day2_effective_time=fields.Char()
    day3_effective_time=fields.Char()
    day4_effective_time=fields.Char()
    day5_effective_time=fields.Char()
    day6_effective_time=fields.Char()
    day7_effective_time=fields.Char()
    absence=fields.Integer()
    delay_time=fields.Integer()
    attendance_bonus=fields.Boolean()
    delay_time_bonus=fields.Boolean()
    total_days_effective_time=fields.Char()
    horas_trabajadas=fields.Float(string="Horas trabajadas")


    @api.onchange('day1_in','day2_in','day3_in','day4_in','day5_in','day6_in','day7_in','day1_out','day2_out','day3_out','day4_out','day5_out','day6_out','day7_out')
    def onchange_calculate_days_worked(self):
        dias_trabajados = 0
        total_retardos=0

        hora_entrada_dia1 = int(self.day1_in.split(":")[0])
        minuto_entrada_dia1 = int(self.day1_in.split(":")[1])
        if hora_entrada_dia1>=7 and minuto_entrada_dia1 >5:
            total_retardos=total_retardos+1

        hora_salida_dia1 = int(self.day1_out.split(":")[0])
        minuto_salida_dia1 = int(self.day1_out.split(":")[1])
        print('El tiempo trabajado es de:')
        dias_trabajados = dias_trabajados + (abs(hora_salida_dia1 - hora_entrada_dia1)) - (abs((minuto_salida_dia1 - minuto_entrada_dia1) / 60))
        print(dias_trabajados)

        hora_entrada_dia2 = int(self.day2_in.split(":")[0])
        minuto_entrada_dia2 = int(self.day2_in.split(":")[1])

        if hora_entrada_dia2>=7 and minuto_entrada_dia2 >5:
            total_retardos=total_retardos+1

        hora_salida_dia2 = int(self.day2_out.split(":")[0])
        minuto_salida_dia2 = int(self.day2_out.split(":")[1])
        print('El tiempo trabajado es de:')
        dias_trabajados = dias_trabajados + (abs(hora_salida_dia2 - hora_entrada_dia2)) - (
                    abs((minuto_salida_dia2 - minuto_entrada_dia2) / 60))
        print(dias_trabajados)

        hora_entrada_dia3 = int(self.day3_in.split(":")[0])
        minuto_entrada_dia3 = int(self.day3_in.split(":")[1])

        if hora_entrada_dia3>=7 and minuto_entrada_dia3 >5:
            total_retardos=total_retardos+1

        hora_salida_dia3 = int(self.day3_out.split(":")[0])
        minuto_salida_dia3 = int(self.day3_out.split(":")[1])
        print('El tiempo trabajado es de:')
        dias_trabajados = dias_trabajados + (abs(hora_salida_dia3 - hora_entrada_dia3)) - ((
                abs(minuto_salida_dia3 - minuto_entrada_dia3) / 60))
        print(dias_trabajados)

        hora_entrada_dia4 = int(self.day4_in.split(":")[0])
        minuto_entrada_dia4 = int(self.day4_in.split(":")[1])
        if hora_entrada_dia4>=7 and minuto_entrada_dia4 >5:
            total_retardos=total_retardos+1

        hora_salida_dia4 = int(self.day4_out.split(":")[0])
        minuto_salida_dia4 = int(self.day4_out.split(":")[1])
        print('El tiempo trabajado es de:')
        dias_trabajados = dias_trabajados + (abs(hora_salida_dia4 - hora_entrada_dia4)) - ((
                abs(minuto_salida_dia4 - minuto_entrada_dia4) / 60))

        hora_entrada_dia5 = int(self.day5_in.split(":")[0])
        minuto_entrada_dia5 = int(self.day5_in.split(":")[1])

        if hora_entrada_dia5>=7 and minuto_entrada_dia5 >5:
            total_retardos=total_retardos+1

        hora_salida_dia5 = int(self.day5_out.split(":")[0])
        minuto_salida_dia5 = int(self.day5_out.split(":")[1])
        print('El tiempo trabajado es de:')
        dias_trabajados = dias_trabajados + (abs(hora_salida_dia5 - hora_entrada_dia5)) - ((
                abs(minuto_salida_dia5 - minuto_entrada_dia5) / 60))
        print(dias_trabajados)

        hora_entrada_dia6 = int(self.day6_in.split(":")[0])
        minuto_entrada_dia6 = int(self.day6_in.split(":")[1])

        if hora_entrada_dia6>=7 and minuto_entrada_dia6 >5:
            total_retardos=total_retardos+1

        hora_salida_dia6 = int(self.day6_out.split(":")[0])
        minuto_salida_dia6 = int(self.day6_out.split(":")[1])
        print('El tiempo trabajado es de:')
        dias_trabajados = dias_trabajados + (abs(hora_salida_dia6 - hora_entrada_dia6)) - ((
                abs(minuto_salida_dia6 - minuto_entrada_dia6) / 60))
        print(dias_trabajados)

        hora_entrada_dia7 = int(self.day7_in.split(":")[0])
        minuto_entrada_dia7 = int(self.day7_in.split(":")[1])
        if hora_entrada_dia7>=7 and minuto_entrada_dia7 >5:
            total_retardos=total_retardos+1

        hora_salida_dia7 = int(self.day7_out.split(":")[0])
        minuto_salida_dia7 = int(self.day7_out.split(":")[1])
        print('El tiempo trabajado es de:')
        dias_trabajados = dias_trabajados + (abs(hora_salida_dia7 - hora_entrada_dia7)) - ((
                abs(minuto_salida_dia7 - minuto_entrada_dia7) / 60))
        print(dias_trabajados)




        print(dias_trabajados)
        f=float(random.randrange(1000))
        print(f)
        if total_retardos>=1:
            self.delay_time_bonus=False
            self.delay_time=total_retardos
        if total_retardos<=0:
            self.delay_time_bonus=True
            self.delay_time = total_retardos

        self.horas_trabajadas=dias_trabajados




    @api.multi
    def open_record(self):
        # first you need to get the id of your record
        # you didn't specify what you want to edit exactly

        rec_id =self.axtraxng_attendance_ids.id
        print(rec_id)
        # then if you have more than one form view then specify the form id
        form_id =1 #self.env.ref('module_name.form_xml_id')

        # then open the form
        return {
            'type': 'ir.actions.act_window',
            'name': 'title',
            'res_model': 'hr.axtraxng_attendance_line',
            'res_id': self.id,#rec_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            #'view_id': form_id.id,
            'context': {},
            # if you want to open the form in edit mode direclty
            'flags': {'initial_mode': 'edit'},
            'target': 'current',
        }




