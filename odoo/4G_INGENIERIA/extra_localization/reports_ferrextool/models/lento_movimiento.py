# -*- coding: utf-8 -*-
from odoo import models, fields, api
#from .reports.exceso_de_inventario import get_report
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from time import time
import io
from http import cookies

global_fariables_of_dates = cookies.SimpleCookie()

class reports_ferrextool_lento_movimiento(models.TransientModel):

    _name = 'reports_ferrextool.lento_movimiento'
    _inherit = 'download.file.base.model'
    start_date = fields.Datetime(store=False)
    end_date = fields.Datetime(store=False)
    

    @api.onchange('start_date')
    def get_start_date(self):
        global_fariables_of_dates["start_date"] = self.start_date
        
    
    @api.onchange('end_date')
    def get_end_date(self):        
        global_fariables_of_dates["end_date"] = self.end_date

    
    def get_filename(self):
        return 'Reporte de Lento Movimiento.xlsx'
        
    
    
    def get_content(self):
        
        tiempo_inicial = time()

             
        output = self.get_report(global_fariables_of_dates["start_date"].value,global_fariables_of_dates["end_date"].value)
        tiempo_final = time()
        tiempo=tiempo_final-tiempo_inicial
        return output.read()

        
    @api.multi
    def Get_stock_move_line_by_date(self,start_date,end_date):
        domain=[('date', '>=',start_date),('date', '<=', end_date)]        
        product = self.env['stock.move.line'].search(domain)
        
        lst_product_id=product.mapped('product_id.id')
        unique_values_lst_allproduct_id=list(set(lst_product_id))
        return unique_values_lst_allproduct_id

    def Get_if_contains_sale(self,id):
        domain=[('product_id', '=',id)]
        try:
            product = self.env['sale.report'].search(domain)
            
            product_detail=product.mapped('product_uom_qty')
            
        except:
            # print('Noooo Tiene venta')
            return id
        if not product_detail:
            return id
        if  product_detail:
            # print('Tiene venta')
            return False

    def Get_product_template(self,id_product):
        lst_poduct_details=[]
        product = self.env['product.product'].browse(id_product)
        
        lst_poduct_details.append(product[0]['name'])
        lst_poduct_details.append(product[0]['standard_price'])
        lst_poduct_details.append(product[0]['qty_available'])
        return lst_poduct_details

    def get_report(self,start_date,end_date):
        lst_withot_sale=[]
        for item in self.Get_stock_move_line_by_date(start_date,end_date):
            venta=self.Get_if_contains_sale(item)
            
            if venta:
                lst_withot_sale.append(venta)

        lst_product_detailed=[]
        for item in lst_withot_sale:
            product = self.Get_product_template(item)
            product_detailed = item, product[0], product[1], product[2]
            lst_product_detailed.append(product_detailed)






        df=pd.DataFrame(lst_product_detailed,columns=['ID','Producto','Precio (C/U)','Cantidad en Stock'])
        df['Costo(MXN)'] = ((df['Precio (C/U)'])*(df['Cantidad en Stock']))
        df =df.drop(df[df['Cantidad en Stock']<=0].index)
        
        towrite = io.BytesIO()
        df.to_excel(towrite)
        towrite.seek(0)
        return towrite