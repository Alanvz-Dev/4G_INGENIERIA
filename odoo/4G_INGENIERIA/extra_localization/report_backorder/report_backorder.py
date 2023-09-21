# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning, except_orm
import base64
from datetime import date, datetime, time, timedelta
import time
from dateutil.relativedelta import relativedelta

class report_backorder(models.Model):
    _name = 'report_backorder.report_backorder'

    @api.multi
    def show_data_report_sale_order(self):
        #self.env.cr.execute("SELECT so.date_from_lead, so.name,rp.name,pp.name_template,sl.price_unit, sl.product_uom_qty, sl.product_uom_qty-sl.qty_invoiced, sl.price_unit*(sl.product_uom_qty-sl.qty_invoiced), so.state FROM sale_order so JOIN sale_order_line sl ON so.id=sl.order_id JOIN product_product pp ON pp.id=sl.product_id JOIN res_partner rp on rp.id=so.partner_id WHERE date_from_lead BETWEEN '2018-01-01' AND current_date AND sl.product_uom_qty > sl.qty_invoiced AND so.state !='cancel' AND so.state !='draft' AND so.state !='sent'; ")
        self.env.cr.execute("SELECT so.date_from_lead, so.name,rp.name,sl.name,sl.price_unit, sl.product_uom_qty, sl.product_uom_qty-sl.qty_invoiced, sl.price_unit*(sl.product_uom_qty-sl.qty_invoiced), so.state FROM sale_order so JOIN sale_order_line sl ON so.id=sl.order_id JOIN product_product pp ON pp.id=sl.product_id JOIN res_partner rp on rp.id=so.partner_id WHERE date_from_lead BETWEEN '2018-01-01' AND current_date AND sl.product_uom_qty > sl.qty_invoiced AND so.state !='cancel' AND so.state !='draft' AND so.state !='sent';")
        report_details = self.env.cr.fetchall()
        report_array = []
        for valores in report_details:
            report_array.append(valores)
        print(report_array)    
        return report_array

    @api.multi
    def show_data_report_sale_order_sum(self):
        self.env.cr.execute("select sum(sl.price_unit*(sl.product_uom_qty-sl.qty_invoiced))FROM sale_order so JOIN sale_order_line sl ON so.id=sl.order_id JOIN product_product pp ON pp.id=sl.product_id WHERE date_from_lead BETWEEN '2020-04-01' AND current_date AND sl.product_uom_qty > sl.qty_invoiced AND so.state !='cancel' AND so.state !='draft' AND so.state !='sent'; ")
        report_details = self.env.cr.fetchall()
        report_array = []
        for valores in report_details:
            report_array.append(valores)
        return report_array

    @api.multi
    def print_kardex(self):
        return {'type': 'ir.actions.report','report_name': 'report_backorder.report_back_order_custom_template','report_type':"qweb-pdf"}
    
    @api.multi
    def print_kardex_xlsx(self):
        return {'type': 'ir.actions.report','report_name': 'reportes_xlsx.report_back_order_xlsx','report_type':"xlsx"}
        
        

    @api.multi
    def limpiar_consulta(self):
        self.producto = 0
        self.fecha_inicio = 0
        self.fecha_fin = 0
        return
