
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
import datetime
import pytz
local_tz = pytz.timezone('America/Mexico_City') 
class ServiceRecord(models.TransientModel):
    _name = 'dining_service.record'
    _description = 'Registrar Servicio de Comedor'

    @api.model
    def record_service(self,barcode):
        barcode=barcode[:-1] 
        date_time_of_record=datetime.datetime.now()
        dining_service_detail = self.env['dining_service.detail'].search([('week', '=', self.get_number_of_week())])
        contract_id = self.env['dining_service.barcode'].get_contract_id_by_barcode(barcode)
        if not contract_id:
            custom_id = self.record_service_custom_barcode(barcode)
            if custom_id:
                return custom_id
            else:
                raise UserError('Código de Barras No Válido')
           
                
        
        line = dining_service_detail.dining_service_line.search([('employee_contract_id','in',[contract_id.id]),('dining_service_detail','in',[dining_service_detail.id])])           
        unique_vals = self.unique_service(line,contract_id.comida_doble)                  
        if isinstance(unique_vals, dict):
            if 'message' in unique_vals:
                return [unique_vals]
        if dining_service_detail:
            if line :
                line.date_time_service_line=[(0, 0, {'date_time':date_time_of_record})]   
            elif not line:
                dining_service_detail.dining_service_line=[(0, 0, {"name":contract_id.name,
                                                              "employee_contract_id":contract_id.id,
                                                              "date_time_service_line":[(0, 0, {'date_time':date_time_of_record})],
                                                              "company":contract_id._cr.dbname,
                                                              'last_update':datetime.datetime.now()  })]                                                                              
        elif not dining_service_detail:
            dining_service_detail = dining_service_detail.create({'name':'SEMANA '+str(self.get_number_of_week()),'week':self.get_number_of_week()})
            dining_service_detail.dining_service_line=[(0, 0, {"name":contract_id.name,
                                                              "employee_contract_id":contract_id.id,
                                                              "date_time_service_line":[(0, 0, {'date_time':date_time_of_record})],
                                                              "company":contract_id._cr.dbname,
                                                              'last_update':datetime.datetime.now()  })]                                                    
             
            ##date_time_of_record.isoformat()
        line = dining_service_detail.dining_service_line.search([('employee_contract_id','in',[contract_id.id]),('dining_service_detail','in',[dining_service_detail.id])])                              
        return {'name':contract_id.name,'image':contract_id.employee_id.image,'count':len(line.date_time_service_line),'barcode':"",'week':dining_service_detail.week}

    def record_service_custom_barcode(self,barcode):
        date_time_of_record=datetime.datetime.now()
        # date_time_of_record='2022-02-24 11:00:00'
        dining_service_detail = self.env['dining_service.detail'].search([('week', '=', self.get_number_of_week())])
        custom_barcode = self.env['dining_service.custom_barcode'].search([('barcode','like','%'+barcode+'%')])
        if not custom_barcode:
            raise UserError('Código de Barras No Válido')


        
        line = dining_service_detail.dining_service_line.search([('employee_contract_id','in',[custom_barcode.numero]),('dining_service_detail','in',[dining_service_detail.id])])   
        unique_vals = self.unique_service(line,False)                  
        if not unique_vals:
            return {'message':'Servicio del Día Realizado'}
        if dining_service_detail:
            if line:
                line.date_time_service_line=[(0, 0, {'date_time':date_time_of_record})]                
            elif not line:
                dining_service_detail.dining_service_line=[(0, 0, {"name":custom_barcode.name,
                                                              "employee_contract_id":custom_barcode.numero,
                                                              "date_time_service_line":[(0, 0, {'date_time':date_time_of_record})],
                                                              "company":'INV/PRACT',
                                                              'last_update':datetime.datetime.now() })]                                                                              
        elif not dining_service_detail:
            dining_service_detail = dining_service_detail.create({'name':'SEMANA '+str(self.get_number_of_week()),'week':self.get_number_of_week()})
            dining_service_detail.dining_service_line=[(0, 0, {"name":custom_barcode.name,
                                                              "employee_contract_id":custom_barcode.numero,
                                                              "date_time_service_line":[(0, 0, {'date_time':date_time_of_record.isoformat()})],
                                                              "company":'INV/PRACT',
                                                              'last_update':datetime.datetime.now()  })]                                                    
             
            
        line = dining_service_detail.dining_service_line.search([('employee_contract_id','in',[custom_barcode.numero]),('dining_service_detail','in',[dining_service_detail.id])])                              
        
        return {'name':custom_barcode.name,'image':(custom_barcode.profile_picture or ""),'count':len(line.date_time_service_line),'barcode':"",'week':dining_service_detail.week}   
        
    def get_number_of_week(self):
        date_today = datetime.date.today()#fecha de l día de hoy
        number_week = date_today.isocalendar()#devuelve el número de la semana iso
        number_day = date_today.isoweekday()#devuelve el número del día de la semana
        if number_day > 3:
            number_week = str(number_week[1] + 1)
        else:
            number_week = str(number_week[1])
        return number_week

    def  unique_service(self,line,comida_doble):
        """
            Verifica que se tenga solo un registro por día en el  modelo dining_service.
            @return: retorna un booleano verdadero en caso de que sea único o que el valor del contrato
            comida_doble sea verdadero
        """
        if line.date_time_service_line:
            line.update({'last_update':datetime.datetime.now()})
            date_today = datetime.datetime.strptime(datetime.date.today().strftime('%Y-%m-%d')+" 00:00:00", '%Y-%m-%d %H:%M:%S')
            today_recs = line.date_time_service_line.search(['&',('date_time_service','in',[line.id]),('date_time','>',date_today.strftime('%Y-%m-%d')+" 00:00:00"),
            ('date_time','<',date_today.strftime('%Y-%m-%d')+" 23:59:59")])
            if len(today_recs) <2 and comida_doble:
                return True,{'line':line.id}
            elif len(today_recs) >=2 and comida_doble:
                return {'message':'El servicio de comedor solo puede aplicarse únicamente dos veces por día con configuración de Recursos Humanos.','line':line.id}
            if today_recs and not comida_doble:
                return {'message':'Servicio del Día registrado previamente','line':line.id}
            elif not today_recs:
                return True
        else:
            return True


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(pytz.UTC)
    return local_tz.normalize(local_dt)