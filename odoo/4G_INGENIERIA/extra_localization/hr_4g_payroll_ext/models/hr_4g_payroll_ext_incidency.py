from datetime import datetime
from xmlrpc.client import boolean
from numpy import char
from odoo import _, api, fields, models
from datetime import timedelta
import math
from odoo.exceptions import ValidationError
import pyodbc
import pandas as pd
import pytz
from odoo.fields import Datetime
HOURS_PER_DAY = 10


class Incidencia(models.Model):
    _name = 'hr_4g_payroll_ext.incidency'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '(Inc4G) Incidencias de Empleados 4G'
    _order = 'date_from desc'
    name = fields.Char(readonly=True,
                       copy=False, default='')
    employee_id = fields.Many2one('hr.employee', track_visibility='onchange',string="Empleado")
    nombre_externo = fields.Char(string='Nombre Completo de La Persona Externa:')
    department = fields.Many2one(related='employee_id.department_id',store=True,string="Departamento")
    tipo = fields.Selection(string='Tipo de Tiempo', selection=[(
        'sum', 'A favor'), ('min', 'En Contra'),('na', 'No Aplica')], track_visibility='onchange')
    state_pago = fields.Selection(string='Estado de Pago', selection=[(
        'done', 'Pagado'), ('draft', 'Pendiente de Pago')], default='draft', track_visibility='onchange')
    dias = fields.Float(track_visibility='onchange',digits = (12,4))
    horas = fields.Float(track_visibility='onchange')
    date_from = fields.Datetime(track_visibility='onchange')
    date_to = fields.Datetime(track_visibility='onchange')
    active = fields.Boolean(default=True, track_visibility='onchange')
    state = fields.Selection(selection=[('done', 'Validado'), (
        'draft', 'Rechazado'), ('pending', 'Para Validar')], default='pending', track_visibility='onchange',string="Estatus RH")
    state_guard = fields.Selection(selection=[('done', 'Aprobado'), (
        'draft', 'No Aprobado')], default='draft', track_visibility='onchange',string="Estatus Gerencia")
    calendario = fields.Many2one(
        'resource.calendar', track_visibility='onchange')
    tipo_incidencia = fields.Selection(selection=[
        ('SUS', 'Suspención'),
        ('EP', 'Entrada a Planta'),
        ('BO', 'Bono'),
        ('BJ', 'Baja'),
        ('HEX1', 'Hora Extra Simple'),
        ('HEX2', 'Hora Extra Doble'),
        ('HEX3', 'Hora Extra Triple'),
        ('TXT', 'Tiempo Por Tiempo'),
        ('FJS', 'Falta Justificada Sin Goce De Sueldo'),
        ('FI', 'Falta Injustificada'),
        ('VAC', 'Vacaciones'),
        ('INC_EG', 'Incapacidad Enfermedad General'),
        ('INC_RT', 'Incapacidad Riesgo de Trabajo'),
        ('INC_MAT', 'Incapacidad Por Maternidad'),
        ('DFES', 'Día Festivo'),
        ('FJC', 'Falta Justificada Con Goce De Sueldo'),
        ('EXT', 'Entrada de Externo')], required=True, track_visibility='onchange')
    nomina_de_pago = fields.Many2one(
        'hr.payslip', string='Nómina', track_visibility='onchange')
    incapacidad_ids = fields.One2many(
        'hr_4g_payroll_ext.incidency_inability', 'incidency_id', track_visibility='onchange')
    entrada_salida_ids = fields.Many2many('hr_4g_payroll_ext.in_out')
    reporte_nomina_ids = fields.Many2one('hr_4g_payroll_ext.reporte_nomina')
    considerar_dias = fields.Boolean(
        string='Considerar Días a 1.4', default=True)
    holiday_id = fields.Many2one('hr.holidays')
    entradas_salidas = fields.Many2many('hr_4g_payroll_ext.in_out_guard',track_visibility='onchange')

    horas_checador = fields.Float(compute='_compute_horas_checador', string='Horas Checador')
    horas_a_considerar = fields.Float(string='Horas a Considerar')
    uuid = fields.Char(string='Identificador Incidencia Masiva')
    monto_bono = fields.Float(string='Monto del Bono',track_visibility='onchange')
    proyecto = fields.Many2one('account.analytic.account',track_visibility='onchange')
    fecha_bono = fields.Date(string='Fecha de Bono',track_visibility='onchange')
    
    @api.one
    def _compute_horas_checador(self):
        if self.entrada_salida_ids:
            self.horas_checador=sum(self.entrada_salida_ids.mapped('tiempo_total_horas'))
            self.update({'horas_a_considerar': sum(self.entrada_salida_ids.mapped('tiempo_total_horas')),'horas_checador':sum(self.entrada_salida_ids.mapped('tiempo_total_horas'))})
        else:            
            self.update({'horas_a_considerar': self.horas,'horas_checador':self.horas
            })            
    
    @api.one
    def valid(self):
        if self.tipo_incidencia not in ['HEX1','HEX2','HEX3','TXT','EP','BO','BJ']:
            if self.tipo_incidencia in ['VAC'] and self.dias <1:
                raise ValidationError(
                "Las Vacaciones deben ser mayores a 1 y sin decimales")

            self.descontar_bonos()
            vals = {"name": self.name,
                        "state": "validate",
                        "user_id": 1,
                        "date_from":self.date_from,
                        "date_to": self.date_to,
                        "holiday_status_id": self.get_id_holiday_status(),
                        "employee_id":self.employee_id.id,
                        "number_of_days_temp":abs(self.dias),
                        "number_of_days":self.dias,
                        "type":'remove',                        
                        "active":True}
            self.holiday_id=self.holiday_id.create(vals).id
            resource_calendar = self.env['resource.calendar.leaves']
            resource_calendar.create({
                'name':self.name,
                'calendar_id':self.calendario.id or self.employee_id.resource_calendar_id.id,
                'date_from':self.date_from,
                'date_to':self.date_to,
                'tz':'Mexico/General',
                'resource_id':self.employee_id.resource_id.id,
                'holiday_id':self.holiday_id.id
            })       
        self.state = 'done'
        

    def reject(self):
        if self.holiday_id:
            self.holiday_id.action_refuse()
            self.holiday_id.action_draft()
            self.holiday_id.sudo().unlink()
        self.state = 'draft'

    def get_id_holiday_status(self):
        return self.env['hr.holidays.status'].search([('name','in',[self.tipo_incidencia])]).id
    
    def descontar_bonos(self):
        if self.tipo_incidencia in ['SUS']:            
            self.employee_id.contract_id.bono_asistencia=False
            self.employee_id.contract_id.bono_puntualidad=False
            self.tipo_incidencia='FI'

    def guard_verification_valid(self):
        for item in self:
            item.state_guard='done'
    
    def guard_verification_cancel(self):
        self.state_guard='draft'


    def register_in(self):
        self.sudo().entradas_salidas=[(0, 0, { 'date_in':fields.datetime.now()})]

    def register_out(self):
        self.sudo().entradas_salidas=[(1, self.entradas_salidas.id, { 'date_out':fields.datetime.now()})]

    @api.multi
    def validacion_multiple(self):
        for item in self:
            try:
                item.valid()
            except Exception as e:
                raise ValidationError(str(e.name+'\t'+item.display_name+'\tID: '+str(item.id)))

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record

            @return: returns a id of new record
        """
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'hr_4g_payroll_ext.incidency') or _('New')
        # values['employee_ids']=False


        result=super(Incidencia, self).create(values)

        return result


    
    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """
        """Realizar el grupo por código y agregarlo al if"""
        # if self.state=='done':
        #     raise ValidationError('No se puede modificar una Incidencia Validada por Recursos Humanos')
        result = super(Incidencia, self).write(values)
    
        return result
    
    
    @api.multi
    def unlink(self):
        """
            Delete all record(s) from recordset
            return True on success, False otherwise
    
            @return: True on success, False otherwise
    
            #TODO: process before delete resource
        """
        for item in self:
            if item.holiday_id:
                item.reject()
        result = super(Incidencia, self).unlink()
    
        return result
    


    @ api.onchange('date_from')
    def _onchange_date_from(self):
        self.onchange_date_from()

    @ api.onchange('horas')
    def _onchange_horas(self):
        # FIX Cuando tenga un calendario el comportamiento va a ser erroneo
        
        if self.considerar_dias:
            self.dias=(round(self.horas)/10)*1.4
            print(self.dias)
        elif not self.considerar_dias:
            self.dias=(round(self.horas)/10)
        if self.tipo=='sum':
            self.dias=abs(self.dias)
        if self.tipo=='min':
            self.dias=abs(self.dias)*-1

    @ api.onchange('considerar_dias')
    def _onchange_considerar_dias(self):
        self._onchange_horas()

    @ api.onchange('tipo_incidencia')
    def _onchange_tipo_incidencia(self):
        if self.tipo_incidencia in ['HEX1', 'HEX2', 'HEX3', 'DFES','BO']:
            self.tipo='sum'
            self._onchange_horas()
            self._onchange_dias()
            # self.tipo='na'
        if self.tipo_incidencia in ['FJS','VAC', 'FI', 'INC_EG', 'INC_RT', 'INC_MAT', 'FJC']:
            self.tipo='min'
            self._onchange_dias()
            self._onchange_horas()
        if self.tipo_incidencia in ['EP','BJ']:
            self.tipo='na'
            self._onchange_dias()
            self._onchange_horas()


    def onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from=self.date_from
        date_to=self.date_to
        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta=fields.Datetime.from_string(
                date_from) + timedelta(hours = HOURS_PER_DAY)
            self.date_to=str(date_to_with_delta)
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp=self._get_number_of_days(
                date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp=0

    @ api.onchange('date_to')
    def _onchange_date_to(self):
        self.onchange_date_to()

    def onchange_date_to(self):
        """ Update the number_of_days. """
        date_from=self.date_from
        date_to=self.date_to
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp=self._get_number_of_days(
                date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp=0

        if self.tipo_incidencia == 'TXT' and self.tipo == 'min':
            self.number_of_days_temp=self.number_of_days_temp*-1
            self.horas=self.horas*-1

        if self.tipo_incidencia == 'TXT' and self.tipo == 'sum':
            self.number_of_days_temp=abs(self.number_of_days_temp)
            self.horas=abs(self.horas)

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        user_tz=pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        from_dt=pytz.utc.localize(
            Datetime.from_string(date_from)).astimezone(user_tz)
        to_dt=pytz.utc.localize(
            Datetime.from_string(date_to)).astimezone(user_tz)

        # if employee_id:
        #     employee = self.env['hr.employee'].browse(employee_id)
        #     res = employee.get_work_days_count(from_dt, to_dt, self.calendario)
        #     # self.dias =round(res['hours']/9.5) ##res['days']
        #     self.horas = res['hours']
        #     print(res)
        #     return self.horas

        time_delta=to_dt - from_dt
        res=((time_delta.days * 86400) + float(time_delta.seconds)) / 3600
        self.horas=res
        return res

    @ api.onchange('calendario')
    def _onchange_calendar(self):
        if self.calendario:
            self.onchange_calendar()

    def onchange_calendar(self):
        if self.employee_id and self.date_from and self.date_to:
            self._get_number_of_days(
                self.date_from, self.date_to, self.employee_id.id)


    @ api.onchange('dias', 'tipo')
    def _onchange_dias(self):
        if self.dias and self.tipo:
            self.onchange_dias()


    def onchange_dias(self):
        if self.tipo == 'min':
            self.horas=abs(self.horas)*-1
        if self.tipo == 'sum':
            self.horas=abs(self.horas)
        elif not self.tipo:
            raise ValidationError(
                "Debe seleccionar el tipo de Hora , A favor o En Contra.")
    @ api.one
    def checador(self):
        user_tz=pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date=pytz.utc.localize(Datetime.from_string(
            self.date_from)).astimezone(user_tz)
        date_to=pytz.utc.localize(Datetime.from_string(
            self.date_to)).astimezone(user_tz)
        print(date)
        fields.Datetime.context_timestamp(
            self, timestamp = fields.Datetime.from_string(self.date_from))
        print(fields.Datetime.context_timestamp(
            self, timestamp=fields.Datetime.from_string(self.date_from)))
        # fields.Datetime.context_timestamp(self,timestamp=self.date_from)
        for item in Checador.Get_Axtrax_Attendandce(self.employee_id.idaxtraxng, date, date_to):
            self.entrada_salida_ids=[(0, 0, item)]


    


class IncidenciaWizardResumenTXT(models.Model):
    _name='hr_4g_payroll_ext.txt_wizard'
    _description='(Inc4G) Reporte INC TXT'
    _rec_name='combination'
    date_from= fields.Datetime(track_visibility = 'onchange')
    date_to= fields.Datetime(track_visibility = 'onchange')
    employee_id=fields.Many2one(
        'hr.employee', track_visibility = 'onchange')
    tipo = fields.Selection(string = 'Tipo de Tiempo', selection =[(
            'sum', 'A favor'), ('min', 'En Contra'),('na', 'No Aplica')], track_visibility = 'onchange')

    state = fields.Selection(string = 'Estatus:', selection =[('done', 'Aprobado'), (
        'draft', 'Rechazado'), ('pending', 'Para Aprobar')], default = 'done', track_visibility ='onchange')
    state_pago = fields.Selection(string = 'Estado de Pago', selection =[(
        'done', 'Pagado'), ('draft', 'Pendiente de Pago')], default = 'draft', track_visibility ='onchange')
    tipo_incidencia = fields.Selection(selection=[
        ('EP', 'Entrada a Planta'),
        ('BO', 'Bono'),
        ('BJ', 'Baja'),
        ('HEX1', 'Hora Extra Simple'),
        ('HEX2', 'Hora Extra Doble'),
        ('HEX3', 'Hora Extra Triple'),
        ('TXT', 'Tiempo Por Tiempo'),
        ('FJS', 'Falta Justificada Sin Goce De Sueldo'),
        ('FI', 'Falta Injustificada'),
        ('VAC', 'Vacaciones'),
        ('INC_EG', 'Incapacidad Enfermedad General'),
        ('INC_RT', 'Incapacidad Riesgo de Trabajo'),
        ('INC_MAT', 'Incapacidad Por Maternidad'),
        ('DFES', 'Día Festivo'),
        ('FJC', 'Falta Justificada Con Goce De Sueldo')], required=True, track_visibility='onchange')
    tipo = fields.Selection(string = 'Tipo de Tiempo', selection =[(
        'sum', 'A favor'), ('min', 'En Contra'),('na', 'No Aplica')], track_visibility = 'onchange')
    busqueda_avanzada=fields.Boolean()
    combination= fields.Char(compute = '_compute_fields_combination')

    @ api.one
    def _compute_fields_combination(self):
        self.combination="Reporte INC"
    def get_resume(self):
        self.ensure_one()
        domain=[]
        if self.date_from:
            domain.append(('date_from', '>', self.date_from))
        if self.date_to:
            domain.append(('date_to', '<', self.date_to))
        if self.employee_id:
            domain.append(('employee_id', 'in', [self.employee_id.id]))
        if self.state:
            domain.append(('state', 'in', [self.state]))
        if self.state_pago:
            domain.append(('state_pago', 'in', [self.state_pago]))
        if self.state_pago:
            domain.append(('tipo_incidencia', 'in', [self.tipo_incidencia]))
        if self.tipo:
            domain.append(('tipo', 'in', [self.tipo]))
        # ids = self.env['hr_4g_payroll_ext.incidency'].search(domain).ids
        print(domain)
        self.env['hr_4g_payroll_ext.incidency_c'].search([]).unlink()
        self.get_resume_by_employee(domain)
        return{
                'name': 'Tiempo a Pagar',
                'view_type': 'form',
                "view_mode": "tree",
                'view_id': False,
                "res_model": "hr_4g_payroll_ext.incidency_c",
                'domain': [('txt_wizard_ids', 'in', [self.id])],
                'type': 'ir.actions.act_window',
            }
        



    def get_resume_by_employee(self, domain):
        incidency=self.env['hr_4g_payroll_ext.incidency']
        incidency_ids = incidency.search(domain)
        data = incidency.read_group(domain, fields=['employee_id', 'horas','dias'], groupby=['employee_id'], orderby="employee_id ASC", lazy=False)
        print(type(data))
        for item in data:
            empleado=self.employee_id.browse(item['employee_id'][0])            
            self.env['hr_4g_payroll_ext.incidency_c'].create({
                'employee_id':empleado.id,
                'horas':item['horas'],
                'dias': item['horas']/9.5,
                'no_cuenta':empleado.no_cuenta,                
                'monto_a_pagar':float("{:.2f}".format(((item['horas']*(empleado.contract_id.sueldo_integrado/8))*self.get_multiplying(self.tipo_incidencia)))),
                'txt_wizard_ids':self.id,
                'tipo_incidencia':self.tipo_incidencia,
                'incid_ids':[(6, 0, incidency_ids.ids)]
            })

    def get_multiplying(self,tipo_incidencia):
        if tipo_incidencia in ['HEX1']:
            return 1
        if tipo_incidencia in ['HEX2']:
            return 2
        if tipo_incidencia in ['HEX3']:
            return 3      

class IncidenciaCalculada(models.Model):
    _name = 'hr_4g_payroll_ext.incidency_c'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Reporte INC TXT'
    txt_wizard_ids = fields.Many2one('hr_4g_payroll_ext.txt_wizard')
    incid_ids = fields.Many2many('hr_4g_payroll_ext.incidency')
    employee_id = fields.Many2one('hr.employee')
    horas = fields.Float()
    dias = fields.Float(digits = (12,4))
    tipo = fields.Selection(string='Tipo de Tiempo', selection=[(
        'sum', 'A favor'), ('min', 'En Contra'),('na', 'No Aplica')], track_visibility='onchange')
    no_cuenta = fields.Char()
    monto_a_pagar = fields.Float()
    tipo_incidencia = fields.Selection(selection=[
        ('EP', 'Entrada a Planta'),
        ('BO', 'Bono'),
        ('BJ', 'Baja'),
        ('HEX1', 'Hora Extra Simple'),
        ('HEX2', 'Hora Extra Doble'),
        ('HEX3', 'Hora Extra Triple'),
        ('TXT', 'Tiempo Por Tiempo'),
        ('FJS', 'Falta Justificada Sin Goce De Sueldo'),
        ('FI', 'Falta Injustificada'),
        ('VAC', 'Vacaciones'),
        ('INC_EG', 'Incapacidad Enfermedad General'),
        ('INC_RT', 'Incapacidad Riesgo de Trabajo'),
        ('INC_MAT', 'Incapacidad Por Maternidad'),
        ('DFES', 'Día Festivo'),
        ('FJC', 'Falta Justificada Con Goce De Sueldo')], required=True, track_visibility='onchange')
    def aplicar_nomina(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Aplicar a Nómina',
            'res_model': 'hr_4g_payroll_ext.aplicar_nomina',
            # 'res_id': self.origen_hoja_de_proyecto.id,#rec_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            # 'view_id': form_id.id,
            'context': self._context,
             'target': 'new',
            # if you want to open the form in edit mode direclty
            'flags': {'initial_mode': 'edit'}
        }



class EntradaSalida(models.Model):
    _name = 'hr_4g_payroll_ext.in_out'
    id_axtraxng = fields.Integer()
    employee_name = fields.Char()
    departamento = fields.Char()
    dia = fields.Char()
    fecha = fields.Date()
    entrada = fields.Char()
    salida = fields.Char()
    tiempo_total = fields.Char()
    tiempo_total_horas = fields.Float()
    



class Checador():
    def Get_Axtrax_Attendandce(id_axtrax, fecha,hasta):
        fecha =fecha-timedelta(minutes=30)
        hasta = hasta+ +timedelta(minutes=30)
        fecha = fecha.strftime("%Y-%m-%d %H:%M:%S.000")
        hasta = hasta.strftime("%Y-%m-%d %H:%M:%S.000")
        server = '192.168.1.1'
        database = 'Axtrax1'
        username = 'sa'
        password = 'a750105530A12345'
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cnxn.cursor()

        # Execute stored procedure
        storedProc = 'SET NOCOUNT ON EXEC	[dbo].[SpAttendaceReport] @listUserId = "' + str(
            id_axtrax) + '", @listReadersId = "1,2", @listOfDays = "1,2,3,4,5,6,7", @autoArrival = 0, @autoExit = 0, @startWorking = "2020-11-09 07:00:00.000", @endWorking = "2020-11-09 17:00:00.000", @overNightOption = 0, @dateFrom = "' + fecha + '", @dateTo = "' + hasta + '"'
        print(storedProc)
        cursor.execute(storedProc)
        rc =cursor.fetchall()
        res=[]
        for item in rc:
            res.append({"id_axtraxng":item[1],"employee_name":item[3],"departamento":item[2],"dia":item[4],"fecha":item[5],"entrada":item[6],"salida":item[7],"tiempo_total":item[8],"tiempo_total_horas":Checador.get_sec(item[8])})
        
        return res

    def get_sec(time_str):
        """Get Seconds from time."""
        h, m = time_str.split(':')
        return int(h) + int(m) / 60


     

