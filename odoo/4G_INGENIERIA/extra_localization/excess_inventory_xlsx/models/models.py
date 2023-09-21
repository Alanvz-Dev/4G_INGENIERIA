# -*- coding: utf-8 -*-
import pickle
from odoo import models, fields, api



class Reportes_Xlsx(models.Model):
    _name = 'excess_inventory_xlsx.excess_inventory_xlsx'
    end_date= fields.Char(default=fields.Datetime.now)
    start_date = fields.Datetime()
    

    @api.onchange('start_date')
    def _value_pc(self):
        global_start_date = open('/globales/global_start_date', 'wb')
        pickle.dump(self.start_date, global_start_date)
        global_start_date.close()



    @api.multi
    def print_kardex_xlsx(self):
        return {'type': 'ir.actions.report','report_name': 'excess_inventory_xlsx.report_excess_inventory_xlsx','report_type':"xlsx"}

    
    def click(self):
        print(self.date)
        self.env['report.excess_inventory_xlsx.report_excess_inventory_xlsx'].generate_xlsx_report()