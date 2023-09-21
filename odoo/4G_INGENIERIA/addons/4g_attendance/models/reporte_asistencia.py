# -*- coding: utf-8 -*-

from odoo import fields, models, api , _
from datetime import datetime, timedelta
from odoo.tools import  pycompat
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
class ReporteAsistencia(models.Model):
    _name = 'reporte.asistencia'
    _description = 'Reporte asistencia'
    _rec_name = 'name'

    name = fields.Char("Nombre")
    fecha_inicial = fields.Date('Fecha inicial')
    fecha_final = fields.Date('Fecha final', store=True)
    asistencia_line_ids = fields.One2many('reporte.asistencia.line','report_asistencia_id',string="Reporte Asistencia lines")
    name = fields.Char("Name", required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho'), ('cancel', 'Cancelado')], string='Estado', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('reporte.asistencia') or '/'
        result=super(ReporteAsistencia,self).create(vals)
        return result


    @api.onchange('fecha_inicial')
    def _get_fecha_final(self):
        if self.fecha_inicial:
            fecha1=datetime.strptime(self.fecha_inicial, "%Y-%m-%d")  + timedelta(days=6)
            fecha1_formato=fecha1.strftime(DEFAULT_SERVER_DATE_FORMAT)
            print(fecha1_formato)
            self.fecha_final = fecha1_formato



    @api.model
    def default_get(self, fields):
        res = super(ReporteAsistencia, self).default_get(fields)

#        employee_ids = self.env['hr.employee'].search([('contract_ids.state','=','open')])
#        employees_id=[];
#        emp_added_ids = []
#        for employee in employee_ids:
#            if employee.id in emp_added_ids:
#                continue
#            employees_id.append((0,0,{'employee_id':employee.id}))
#            emp_added_ids.append(employee.id)
#        res['asistencia_line_ids'] = employees_id
        return res

    @api.multi
    def action_validar(self):
        self.write({'state':'done'})
        return

    @api.multi
    def action_cancelar(self):
        self.write({'state':'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state':'draft'})

#     @api.multi
#     @api.onchange('fecha_inicial')
#     def set_all_employee(self):
#         if self.fecha_inicial:
#             employee_ids = self.env['hr.employee'].search([('contract_ids.state','=','open')])
#             repo_assi_obj=self.env['reporte.asistencia.line']
#             employees_id=[];
#             for employee in employee_ids:
#                 line =  repo_assi_obj.create({'employee_id':employee.id})
#                 employees_id.append(line.id)
#             list_set = set(employees_id)
#             employees_id = (list(list_set))      
#             self.asistencia_line_ids=employees_id   

    @api.multi
    def calcular_todo(self):
        self.calculate_attendance()        
        self.calculate_faltas()
        self.calculate_dias_laborados()
        self.calculate_bonos()
    @api.multi
    def calculate_faltas(self):
        cr = self._cr
        fecha_inicial=datetime.strptime(self.fecha_inicial, "%Y-%m-%d")
        fechas_de_nomina=[]
        fecha_y_horas_de_llegada=[]
        fecha=fecha_inicial
        fechas_de_nomina.append(fecha)
        for i in range(6):
            fecha=fecha+timedelta(days=1)
            fechas_de_nomina.append(fecha)
        for item in range(len(self.asistencia_line_ids.ids)):
            fecha_y_horas_de_llegada=[]
            nn=self.env['reporte.asistencia.line'].browse(self.asistencia_line_ids.ids[item])
            print(nn)
            for item0 in fechas_de_nomina:
                print(type(item0))
                f1=str(item0)
                
                f=f1[0]+f1[1]+f1[2]+f1[3]+f1[4]+f1[5]+f1[6]+f1[7]+f1[8]+f1[9]
                
                queryy="select check_in from hr_attendance where check_in BETWEEN '" +str(item0)+ "' and '"+str(f)+ " 23:59:59' and employee_id="+str(nn.employee_id.id)+" order by check_in ASC LIMIT 1"
                cr.execute(queryy)
                xx = cr.fetchall()
                try:
                    fecha_y_horas_de_llegada.append(xx[0])
                except:fecha_y_horas_de_llegada.append('')
            
            if fecha_y_horas_de_llegada[0]=='':
                nn.write({'day_1_entrada':fecha_y_horas_de_llegada[0]})
            else:
                nn.write({'day_1_entrada':fecha_y_horas_de_llegada[0][0]})
                

            if fecha_y_horas_de_llegada[1]=='':
                nn.write({'day_2_entrada':fecha_y_horas_de_llegada[1]})
            else:
                nn.write({'day_2_entrada':fecha_y_horas_de_llegada[1][0]})

                
            if fecha_y_horas_de_llegada[2]=='':
                nn.write({'day_3_entrada':fecha_y_horas_de_llegada[2]})
            else:
                nn.write({'day_3_entrada':fecha_y_horas_de_llegada[2][0]})

            if fecha_y_horas_de_llegada[3]=='':
                nn.write({'day_4_entrada':fecha_y_horas_de_llegada[3]})
            else:
                nn.write({'day_4_entrada':fecha_y_horas_de_llegada[3][0]})

            if fecha_y_horas_de_llegada[4]=='':
                nn.write({'day_5_entrada':fecha_y_horas_de_llegada[4]})
            else:
                nn.write({'day_5_entrada':fecha_y_horas_de_llegada[4][0]})

            if fecha_y_horas_de_llegada[5]=='':
                nn.write({'day_6_entrada':fecha_y_horas_de_llegada[5]})
            else:
                nn.write({'day_6_entrada':fecha_y_horas_de_llegada[5][0]})
                
            if fecha_y_horas_de_llegada[6]=='':
                nn.write({'day_7_entrada':fecha_y_horas_de_llegada[6]})
            else:
                nn.write({'day_7_entrada':fecha_y_horas_de_llegada[6][0]})

    @api.multi
    def calculate_dias_laborados(self):
        for item in range(len(self.asistencia_line_ids.ids)):
            dias_lab=[]
            total_de_dias_laborados=0
            nn=self.env['reporte.asistencia.line'].browse(self.asistencia_line_ids.ids[item])
            dias_lab.append(nn.day_1)
            dias_lab.append(nn.day_2)
            dias_lab.append(nn.day_3)
            dias_lab.append(nn.day_4)
            dias_lab.append(nn.day_5)
            dias_lab.append(nn.day_6)
            dias_lab.append(nn.day_7)
            for items in range(len(dias_lab)):
                if dias_lab[items]>=9.25:
                    dias_lab[items]=9.25
                total_de_dias_laborados=total_de_dias_laborados+dias_lab[items]
            
                    

            nn.write({'dias_lab':str((total_de_dias_laborados/46.25)*7)})
            print((total_de_dias_laborados/46.25)*7)

    @api.multi
    def calculate_bonos(self):
        for item in range(len(self.asistencia_line_ids.ids)):
            entradas_de_usuario=[]
            nn=self.env['reporte.asistencia.line'].browse(self.asistencia_line_ids.ids[item])
            #if nn.modificado_manualmente==False:
            if True:

            
                if nn.day_1_entrada==False or nn.day_1_entrada=='':
                    entradas_de_usuario.append(False)
                else:
                    hora_de_entrada_de_usuario=datetime.strptime(nn.day_1_entrada,'%Y-%m-%d %H:%M:%S')
                    entradas_de_usuario.append(hora_de_entrada_de_usuario)

                            #nn=self.env['reporte.asistencia.line'].browse(self.asistencia_line_ids.ids[item])
                if nn.day_2_entrada ==False or nn.day_2_entrada =='':
                    entradas_de_usuario.append(False)
                else:                
                    hora_de_entrada_de_usuario=datetime.strptime(nn.day_2_entrada,'%Y-%m-%d %H:%M:%S')
                    entradas_de_usuario.append(hora_de_entrada_de_usuario)

                if nn.day_3_entrada ==False or nn.day_3_entrada =='':
                    entradas_de_usuario.append(False)
                else:
                    hora_de_entrada_de_usuario=datetime.strptime(nn.day_3_entrada,'%Y-%m-%d %H:%M:%S')
                    entradas_de_usuario.append(hora_de_entrada_de_usuario)

                if nn.day_4_entrada ==False or nn.day_4_entrada =='':
                    entradas_de_usuario.append(False)
                else:
                    hora_de_entrada_de_usuario=datetime.strptime(nn.day_4_entrada,'%Y-%m-%d %H:%M:%S')
                    entradas_de_usuario.append(hora_de_entrada_de_usuario)

                if nn.day_5_entrada ==False or nn.day_5_entrada =='':
                    entradas_de_usuario.append(False)
                else:                
                    hora_de_entrada_de_usuario=datetime.strptime(nn.day_5_entrada,'%Y-%m-%d %H:%M:%S')
                    entradas_de_usuario.append(hora_de_entrada_de_usuario)

                if nn.day_6_entrada ==False or nn.day_6_entrada =='':
                    entradas_de_usuario.append(False)
                else:
                    hora_de_entrada_de_usuario=datetime.strptime(nn.day_6_entrada,'%Y-%m-%d %H:%M:%S')
                    entradas_de_usuario.append(hora_de_entrada_de_usuario)

                if nn.day_7_entrada ==False or nn.day_7_entrada=='':
                    entradas_de_usuario.append(False)
                else:

                    hora_de_entrada_de_usuario=datetime.strptime(nn.day_7_entrada,'%Y-%m-%d %H:%M:%S')
                    entradas_de_usuario.append(hora_de_entrada_de_usuario)
                print(entradas_de_usuario)
                faltas=0
                retardos=0
                for _item in range(len(entradas_de_usuario)):

                    cadena_entrada=str(entradas_de_usuario[_item])

                    if entradas_de_usuario[_item]==False:                   
                        faltas=faltas+1
                    if entradas_de_usuario[_item]=='':                   
                        faltas=faltas+1
                    if cadena_entrada=='False':
                        retardos=retardos+1
                    if entradas_de_usuario[_item] != 0:
                        if entradas_de_usuario[_item]>datetime.strptime(cadena_entrada[0]+cadena_entrada[1]+cadena_entrada[2]+cadena_entrada[3]+cadena_entrada[4]+cadena_entrada[5]+cadena_entrada[6]+cadena_entrada[7]+cadena_entrada[8]+cadena_entrada[9]+" 07:05:00",'%Y-%m-%d %H:%M:%S'):
                            retardos=retardos+1
                            nn.write({'bono_de_puntualidad':False})

                if entradas_de_usuario[1]==False:
                    if faltas>0:
                        faltas=faltas-1
                if entradas_de_usuario[2]==False:
                    if faltas>0:
                        faltas=faltas-1

                if entradas_de_usuario[1]==0:
                    if retardos>0:
                        retardos=retardos-1
                if entradas_de_usuario[2]==0:

                    if retardos>0:
                        retardos=retardos-1

                contrato_empleado=self.env['hr.contract'].search([('employee_id','=',nn.employee_id.id)])
                if faltas>0:
                        nn.write({'bono_de_puntualidad':False})
                        nn.write({'bono_de_asistencia':False})
                        contrato_empleado.write({'bono_puntualidad':False})
                        contrato_empleado.write({'bono_asistencia':False})
                else:
                    nn.write({'bono_de_asistencia':True})
                    contrato_empleado.write({'bono_asistencia':True})

                if retardos>0:                    
                        contrato_empleado.write({'bono_puntualidad':False})
                        contrato_empleado.write({'bono_puntualidad':False})                    
                else:
                    contrato_empleado.write({'bono_puntualidad':True})
                    nn.write({'bono_de_puntualidad':True})


                nn.write({'faltas':str(faltas)})
                nn.write({'retardos':str(retardos)})
                faltas=0
                
    @api.multi
    def calculate_attendance(self):
        if not self.fecha_inicial or not self.fecha_final:
            raise UserError(_('Falta seleccionar fecha inicial y final'))

        fecha_inicial = datetime.strptime(self.fecha_inicial,'%Y-%m-%d')
        check_out = fecha_inicial + relativedelta(days=6)

        employee_ids = self.env['hr.employee'].search([('contract_ids.state','=','open')])
        employees_id=[];
        emp_added_ids = []
        for employee in employee_ids:
            if employee.id in emp_added_ids:
                continue
            employees_id.append((0,0,{'employee_id':employee.id}))
            #self.asistencia_line_ids.employee_id += employee
            emp_added_ids.append(employee.id)
        self.asistencia_line_ids = employees_id

        employees = self.asistencia_line_ids.mapped('employee_id')
        employees_ids = employees.ids
#         attendances = self.env['hr.attendance'].search([('name','>=', fecha_inicial),
#                                                         ('name','<=', end_date),
#                                                         ('employee_id','in', employees.ids)
#                                                         ])
        cr = self._cr
        if employees_ids:
            employees_ids = str(employees_ids)
            employees_ids = employees_ids[1:len(employees_ids)-1] 
            cr.execute("""select employee_id, sum(worked_hours), check_in::date from hr_attendance 
                        where check_in::date>='%s' and check_in::date <= '%s' and employee_id in (%s)
                        group by employee_id, check_in::date order by check_in::date 
                        """%((fecha_inicial.strftime('%Y-%m-%d'), check_out.strftime('%Y-%m-%d'), employees_ids)))
            employee_data = cr.fetchall()
            employee_data_dict = {}
            for data in employee_data:
                employee_id = data[0]
                worked_hours = data[1]
                att_date = data[2]
                if employee_id not in employee_data_dict:
                    employee_data_dict.update({employee_id:{}})
                
                employee_data_dict[employee_id][att_date] = worked_hours
            days_dict = {'day_1':0, 'day_2':1, 'day_3':2, 'day_4':3, 'day_5': 4, 'day_6': 5, 'day_7': 6}    
            for line in self.asistencia_line_ids:
                employee_id = line.employee_id.id
                emp_data = employee_data_dict.get(employee_id)
                if emp_data:
                    vals = {}
                    for day_field, day in  days_dict.items():
                        day_date = fecha_inicial + relativedelta(days=day)
                        day_date = day_date.strftime('%Y-%m-%d')
                        if day_date in emp_data:
                            vals.update({day_field: emp_data[day_date]})
                    if vals:
                        line.write(vals)
        return True

class ReporteAsistenciaLine(models.Model):
    _name = 'reporte.asistencia.line'
    
    hr_dia= 9.25
    report_asistencia_id = fields.Many2one('reporte.asistencia','Report Asistencia')
    employee_id = fields.Many2one('hr.employee','Empleado')
    day_1=fields.Float('D1')
    day_2=fields.Float('D2')
    day_3=fields.Float('D3')
    day_4=fields.Float('D4')
    day_5=fields.Float('D5')
    day_6=fields.Float('D6')
    day_7=fields.Float('D7')
    day_1_entrada=fields.Char('Llegada dia 1')
    day_2_entrada=fields.Char('Llegada dia 2')
    day_3_entrada=fields.Char('Llegada dia 3')
    day_4_entrada=fields.Char('Llegada dia 4')
    day_5_entrada=fields.Char('Llegada dia 5')
    day_6_entrada=fields.Char('Llegada dia 6')
    day_7_entrada=fields.Char('Llegada dia 7')
    faltas=fields.Integer('Faltas')
    retardos=fields.Integer('Retardos')
    dias_lab=fields.Float('Dias laborados', store=True, readonly=True)
    bono_de_asistencia=fields.Boolean(default=True,store=True)
    bono_de_puntualidad=fields.Boolean(default=True,store=True)
    modificado_manualmente=fields.Boolean()

    @api.multi
    @api.onchange('day_1','day_2','day_3','day_4','day_5','day_6','day_7','bono_de_asistencia','bono_de_puntualidad')
    def _update_table(self):
        cr = self._cr
        queryy="select id from reporte_asistencia where fecha_inicial='"+str(self.report_asistencia_id.fecha_inicial)+"' and fecha_final='"+str(self.report_asistencia_id.fecha_final)+"'"
        cr.execute(queryy)
        id_line_ids = cr.fetchall()
        print(str(id_line_ids[0]))
        print(id_line_ids)
        print(self.employee_id.id)
        queryy2="select id from reporte_asistencia_line where report_asistencia_id= "+str(id_line_ids[0][0])+" and employee_id="+str(self.employee_id.id)
        print(queryy2)
        cr.execute(queryy2)
        id_line_ids2 = cr.fetchall()
        print(self.report_asistencia_id)          
        nn=self.env['reporte.asistencia.line'].browse(int(id_line_ids2[0][0]))
        dias_lab=[]
        total_de_dias_laborados=0
        dias_lab.append(nn.day_1)
        dias_lab.append(nn.day_2)
        dias_lab.append(nn.day_3)
        dias_lab.append(nn.day_4)
        dias_lab.append(nn.day_5)
        dias_lab.append(nn.day_6)
        dias_lab.append(nn.day_7)
        for items in range(len(dias_lab)):
            if dias_lab[items]>=9.25:
                dias_lab[items]=9.25
            total_de_dias_laborados=total_de_dias_laborados+dias_lab[items]                
        nn.write({'dias_lab':str((total_de_dias_laborados/46.25)*7)})
        nn.write({'day_1':str(dias_lab[0])})
        nn.write({'day_2':str(dias_lab[1])})
        nn.write({'day_3':str(dias_lab[2])})
        nn.write({'day_4':str(dias_lab[3])})
        nn.write({'day_5':str(dias_lab[4])})
        nn.write({'day_6':str(dias_lab[5])})
        nn.write({'day_7':str(dias_lab[6])})
        contrato_empleado=self.env['hr.contract'].search([('employee_id','=',nn.employee_id.id)])
        contrato_empleado.write({'bono_puntualidad':self.bono_de_puntualidad})
        contrato_empleado.write({'bono_asistencia':self.bono_de_asistencia})
        nn.write({'modificado_manualmente':True})
        print(nn)
        
    
    

        



        
                




        
