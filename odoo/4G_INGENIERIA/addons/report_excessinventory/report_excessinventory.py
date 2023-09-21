# -*- coding: utf-8 -*-


from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import UserError, RedirectWarning, ValidationError, except_orm
import base64
from datetime import date, datetime, time, timedelta
import time
from dateutil.relativedelta import relativedelta


class report_excessinventory(models.Model):
    _name = 'report.excessinventory'
    fecha_inicio = fields.Datetime('Fecha inicio:')

    @api.multi
    def show_data_report_stock(self):
        fecha_i = datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S")
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")

        report_array = []
        self.env.cr.execute("select pp.name_template,pt.cost_product,(select sum(sq.qty) from stock_quant sq  join stock_location sl on sl.id=sq.location_id where sl.usage='internal' and sq.in_date between %s and current_date and sq.product_id=pp.id) as stock, (select sum(sm.product_uom_qty) from stock_move sm  where pp.id=sm.product_id and  sm.date between %s and current_date and sm.location_dest_id=9) from product_product pp join stock_move sm on pp.id=sm.product_id join stock_quant sq on sq.product_id=pp.id join product_template pt on pt.id=pp.product_tmpl_id where (select sum(sq.qty) from stock_quant sq  join stock_location sl on sl.id=sq.location_id  where sl.usage='internal' and sq.in_date between %s and current_date and sq.product_id=pp.id) > (select sum(sm.product_uom_qty) from stock_move sm  where pp.id=sm.product_id and  sm.date between %s and current_date and sm.location_dest_id=9) and sm.date between %s and current_date group by pp.id,pt.cost_product;", (f_i, f_i, f_i, f_i, f_i))
        report_details = self.env.cr.fetchall()
        for valores in report_details:
            print ("valoresssssssssssssssssssssssssss:_______________:::::::::::>", valores)
            report_array.append(valores)
        return report_array

    @api.multi
    def print_excessinventory(self):
        return self.env['report'].get_action(self, 'report_excessinventory.template_report_excessinventory')

    @api.multi
    def limpiar_consulta(self):
        self.fecha_inicio = 0
        self.fecha_fin = 0
        return