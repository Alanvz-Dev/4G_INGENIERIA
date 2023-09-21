# -*- coding: utf-8 -*-
from odoo import fields, models, api 
import base64
import datetime
from odoo.exceptions import Warning
from .tzlocal import get_localzone


try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None
    
import pytz
import logging
_logger = logging.getLogger(__name__)

class RemainImportAttendance(models.TransientModel):
    _name='remain.import.attendance'
    
    employee_id = fields.Many2one('hr.employee',string='Empleado')
    line_no = fields.Char('Numero de linea')
    date = fields.Char('Fecha')
    error_text = fields.Char(string='Error')
    

class ImportAttendance(models.TransientModel):
    _name='import.attendance'
    
    import_file = fields.Binary("Import Excel File",required=False)
    file_name = fields.Char("Filename")
    
   
    @api.multi
    def import_attendance(self):
        hr_attendance_obj = self.env['hr.attendance']
        hr_employee_obj = self.env['hr.employee']
        if not self.import_file:
            raise Warning("Selecione primero un archivo.")

        book = xlrd.open_workbook(file_contents=base64.decodestring(self.import_file))
        for sheet in book.sheets():
            user_name = ''
            department=''
            line = 0
            user_attandance_dic = {}
            attendance_data_list=[]
            for row in map(sheet.row, range(sheet.nrows)):
                line += 1
                values = []
                for cell in row:
                    if cell.ctype is xlrd.XL_CELL_DATE:
                        is_datetime = cell.value % 1 != 0.0
                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                        print(dt)
                        print(dt.strftime('%Y-%m-%d %H:%M:%S'))
                        if is_datetime:
                            values.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            print(dt)
                            values.append(dt.strftime('%Y-%m-%d'))
                    else:
                        values.append(cell.value)

                if 'Fecha' not in values:
                    if 'Departamento' in str(values):
                        department=values[0]
                    if 'Nombre de usuario' in str(values):
                        user_name=values[1]

                if '1\Panel 1\Lector 1' in values:
                    data_list=[line,department,user_name,values[2],values[3],'check_out']
                    attendance_data_list.append(data_list)
                if '1\Panel 1\Lector 2' in values:
                    data_list=[line,department,user_name,values[2],values[3],'check_in']
                    attendance_data_list.append(data_list)
                if  values==['', '', '', '', '']:
                    if attendance_data_list:
                        attendance_data_list = [list(x) for x in set(tuple(x) for x in attendance_data_list)]
                        attendance_data_list.sort(key = lambda x: x[3]) 
                        user_attandance_dic.update({user_name:attendance_data_list})
                        attendance_data_list=[]  

            final_attendance_dict = {}
            new_final_attendance_dict={}
            for key,values in user_attandance_dic.items():
                is_check_in=True
                is_check_checkout=False
                data_list = values
                for list_data in data_list:
                    if 'check_in' in str(list_data):
                        if is_check_in:
                            is_check_in=False
                            is_check_checkout=True
                            attendance_dict={}
                            attendance_dict[list_data[0]]=list_data
                            date_key=list_data[3].replace(':',"_")
                            final_attendance_dict[date_key]=attendance_dict
                        else:
                            self.employee_error_attendance_create(list_data)
                    else:
                        if is_check_checkout:
                            is_check_checkout=False
                            attendance_dict[list_data[0]]=list_data
                            final_attendance_dict[date_key]=attendance_dict
                            is_check_in=True
                        else:
                            self.employee_error_attendance_create(list_data)
                new_final_attendance_dict[key]=final_attendance_dict
                final_attendance_dict={}    
            print (new_final_attendance_dict)

        user_attance_dict={}
        for key,values in new_final_attendance_dict.items():
            employee_name = key.split("Nombre de usuario:")[1]
            employee_data = hr_employee_obj.search([('name','=',employee_name.replace(',','').strip())])
            if employee_data:
                employee_id=employee_data.id
            else:
                continue
#                employee_data=hr_employee_obj.create({'name':employee_name.strip()})
#                employee_id=employee_data.id
            user_wise_data=[]
            for key,values_1 in values.items():
                if len(values_1.items())==2:
                    dict_key_of=[]
                    for k,v in values_1.items():
                        dict_key_of.append(k)
                    dict_key_of.sort(key=None, reverse=False)
                    check_in_date_obj = datetime.datetime.strptime(values_1[dict_key_of[0]][3],'%Y-%m-%d %H:%M:%S')
                    check_out_date_obj=datetime.datetime.strptime(values_1[dict_key_of[1]][3],'%Y-%m-%d %H:%M:%S')
                    print(check_in_date_obj)
                    print(check_out_date_obj)
                    data={'employee_id':employee_id,
#                          'check_in':check_in_date_obj.astimezone(pytz.timezone(self.env.user.tz or 'UTC')),
#                          'check_out':check_out_date_obj.astimezone(pytz.timezone(self.env.user.tz or 'UTC'))} 
                            'check_in':self.get_user_time_zone(check_in_date_obj),
                            'check_out':self.get_user_time_zone(check_out_date_obj)}

                    user_wise_data.append(data)
            user_attance_dict[employee_data.name]=user_wise_data

        for key,values in user_attance_dict.items():
            for data in values:
                hr_attendance_obj.create(data)

        return

    def employee_error_attendance_create(self,list_data):
        hr_employee_obj = self.env['hr.employee']
        remain_import_attendance_obj = self.env['remain.import.attendance']
        employee_name=list_data[2].split("Nombre de usuario:")[1]
        employee_data = hr_employee_obj.search([('name','=',employee_name.replace(',','').strip())])
        if employee_data:
            employee_id=employee_data.id
       # else:
       #     continue
        #    employee_data=hr_employee_obj.create({'name':employee_name.strip()})
        #    employee_id=employee_data.id
            remain_import_attendance_obj.create({'employee_id':employee_id,
                                         'line_no':list_data[0],
                                         'date':list_data[3],
                                         'error_text':"invalid "+list_data[5] +" entry"})
            return True
    
    
    def get_user_time_zone(self,naive):
        timezone = self.env.user.tz or self._context.get('tz') or 'UTC'
        print(timezone)
        local = pytz.timezone(timezone)
        print(local)
        local_dt = local.localize(naive, is_dst=None)
        print(local_dt)
        utc_dt = local_dt.astimezone (pytz.utc)
        print(utc_dt)
        utc_date = utc_dt.strftime ("%Y-%m-%d %H:%M:%S")
        print(utc_date)
        print(local_dt)
        return local_dt