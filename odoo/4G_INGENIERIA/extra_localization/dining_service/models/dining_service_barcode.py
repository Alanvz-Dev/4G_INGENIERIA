from .dining_service_barcode_cnn import get_contract_name
from odoo import models, fields, api
from odoo.modules.registry import Registry
import random
import base64
from io import BytesIO
import zipfile
from barcode import EAN13
import barcode as c_barcode
from barcode.writer import ImageWriter


class generate_barcode_by_contract(models.Model):
    _name = 'dining_service.barcode'
    contracts_info = fields.Selection('_get_reference_contract',string='Empleados')
    binary = fields.Binary('Binray')
    binary_fname = fields.Char('Binary Name')
    contract_ids = fields.Many2many('hr.contract',string='Empleados')
    
    
    def _get_reference_contract(self):
        try:
            lst = list()
            databases = [{'db':'4G_INGENIERIA','url':'http://odoo.4gingenieria.com/'}, {'db':'FERREXTOOL','url':'http://odoo.ferrextool.com.mx/'}]
            for database in databases:
                print(database['db'],database['url'])
                lst=lst+get_contract_name(database['db'],database['url'])
            return lst
        except Exception as e:
            print(e)

   
    def barcode_by_company(self):
        try:
            lst = []
            databases = ['4G_INGENIERIA', 'FERREXTOOL']
            for database in databases:
                try:
                    registry = Registry(database)
                    cr = registry.cursor()
                    env = api.Environment(cr, self.env.uid, {})
                    contracts = env['hr.contract'].sudo().search([('state', 'in', ['open']),('employee_id', '!=',False)])
                    for contact in contracts:
                        if contact.dinning_service_barcode == '' or contact.dinning_service_barcode is None or contact.dinning_service_barcode is False:
                            contact.dinning_service_barcode = str(random.randint(111111111111, 999999999999))
                            cr.commit()
                        rec_val = (self.generate_barcode(contact.dinning_service_barcode, str(
                            contact.name+' '+database)), contact.name+'.png')
                        lst.append(rec_val)
                    cr.close()
                    env.reset()
                except:
                    pass
            self.binary =self.generate_zip_base_64(lst)
            self.binary_fname='Codigos_De_Todos_Los_Empleados'+'.zip'
        except:
            pass

    def barcode_by_contract(self):
        try:
            contracts_info = self._get_reference_contract()
            database = ''
            current_contract=[]
            for contract in contracts_info:
                if contract[0] == int(self.contracts_info):
                    database = contract[1].split('/')
                    current_contract.append(contract)
                    break
            registry = Registry(database[1])
            cr = registry.cursor()
            env = api.Environment(cr, self.env.uid, {})
            contracts = env['hr.contract'].sudo().search([('state', 'in', ['open']), ('id', 'in', [int(self.contracts_info)])])
            for contact in contracts:
                if contact.dinning_service_barcode == '' or contact.dinning_service_barcode is None or contact.dinning_service_barcode is False:
                    contact.dinning_service_barcode = str(random.randint(111111111111, 999999999999))
                    cr.commit()
            cr.close()
            env.reset()
            self.binary = base64.b64encode(self.generate_barcode(contact.dinning_service_barcode,database[0]+' '+database[1]))
            self.binary_fname = str(database[0])+str(database[1])+'.png'
        except:
            pass

    def barcode_manual_by_contract(self):
        try:
            self._get_reference_contract()
            action = self.env['dining_service.detail'].find_res_partner_by_ref_manual(self.contracts_info)
            return action
        except:
            pass
        

    def generate_zip_base_64(self, files):
        mem_zip = BytesIO()

        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.writestr(f[1], f[0])
        return base64.b64encode(mem_zip.getvalue())

    def generate_barcode(self, barcode, text):
        file = ''
        buffered = BytesIO()
        barcode_format = c_barcode.get_barcode_class('ean13')
        my_barcode = barcode_format(barcode, writer=ImageWriter())
        output = my_barcode.render(
            writer_options={"module_width":0.35, "module_height":10, "font_size": 3, "text_distance": 1, "quiet_zone": 1},
            text=text)
        output.save(buffered, format="PNG")
        file = buffered.getvalue()
        buffered.close()
        return file



    def clear_data(self):
        pass


    def get_contract_id_by_barcode(self,barcode):       
        databases = ['4G_INGENIERIA', 'FERREXTOOL']        
        for database in databases:
            try:
                registry = Registry(database)
                cr = registry.cursor()
                env = api.Environment(cr, self.env.uid, {})
                contract = env['hr.contract'].sudo().search([('dinning_service_barcode','like','%'+barcode+'%')])
                if contract:
                    # cr.commit()
                    # cr.close()
                    # env.reset()
                    return contract
                    # continue
            except:
                pass




