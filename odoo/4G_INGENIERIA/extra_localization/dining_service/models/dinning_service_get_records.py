from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
from odoo.modules.registry import Registry
import datetime
import json

class ServiceRecord(models.TransientModel):
    _name = 'dining_service.get_record'
    _description = 'Obtener Lista de Comedor'

    @api.model
    def get_records(self):
        
        dining_service_detail = self.env['dining_service.detail'].search([('week', '=', self.env['dining_service.record'].get_number_of_week())])
        list=[]
        
        databases = ['4G_INGENIERIA', 'FERREXTOOL']
        for database in databases:
            try:

                registry = Registry(database)
                cr = registry.cursor()
                env = api.Environment(cr, self.env.uid, {})
                contracts = env['hr.contract'].sudo().search([('state','in',['open'])])
                for contract_id in contracts:
                    line = dining_service_detail.dining_service_line.search([('employee_contract_id','in',[contract_id.id]),('dining_service_detail','in',[dining_service_detail.id])])                              
                    list.append({'name':contract_id.name,'image':(contract_id.employee_id.image or ""),'count':len(line),'barcode':(contract_id.dinning_service_barcode or "")})
                cr.close()
                env.reset()
            except:
                pass
        result = {"MetaData": {}, "top": list}
        # print(json.dumps(result, sort_keys=True, indent=4))
        return result