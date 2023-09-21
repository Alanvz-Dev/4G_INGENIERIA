# -*- coding: utf-8 -*-
import pickle
from odoo import models, fields, api



class Reportes_Xlsx(models.Model):
    _name = 'slow_movement_xlsx.slow_movement_xlsx'
    end_date= fields.Datetime()
    start_date = fields.Datetime()
    

    @api.onchange('start_date')
    def _value_pc2(self):
        global_start_date = open('/globales/global_start_date', 'wb')
        pickle.dump(self.start_date, global_start_date)
        global_start_date.close()

    @api.onchange('end_date')
    def _value_pc(self):
        global_end_date = open('/globales/global_end_date', 'wb')
        pickle.dump(self.end_date, global_end_date)
        global_end_date.close()



    @api.multi
    def print_kardex_xlsx(self):
        return {'type': 'ir.actions.report','report_name': 'slow_movement_xlsx.report_slow_movement_xlsx','report_type':"xlsx"}

    
    def click(self):
        print(self.date)
        self.env['report.slow_movement_xlsx.report_slow_movement_xlsx'].generate_xlsx_report()