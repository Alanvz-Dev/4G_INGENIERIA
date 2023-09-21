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


class reports_ferrextool_exceso_de_inventario(models.TransientModel):

    _name = 'reports_ferrextool.exceso_de_inventario'
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
        return 'Reporte Exceso de Inventario.xlsx'
        
    
    
    def get_content(self):
        tiempo_inicial = time()

        print(1)        
        output = self.get_report(global_fariables_of_dates["start_date"].value,global_fariables_of_dates["end_date"].value)
        print(type(output))
        tiempo_final = time()
        tiempo=tiempo_final-tiempo_inicial
        print(tiempo)
        return output.read()

        
    @api.multi
    def Get_stock_move_line_by_date(self,start_date,end_date):
        domain=[('state', '=', 'done'),('location_dest_id', '=', 9),('date', '>=',start_date),('date', '<=', end_date)]        
        product = self.env['stock.move.line'].search(domain)
        lst_product_id=product.mapped('product_id.id')
        lst_product_qty_done=product.mapped('qty_done')
        
        lst_product_detail=[]
        for i in range(len(lst_product_id)):
            product_detail=lst_product_id[i],lst_product_qty_done[i]
            lst_product_detail.append(product_detail)
        
        return lst_product_detail

    def Get_product_template(self,id_product):
        lst_poduct_details=[]
        domain=[('id', '=', id_product)]
        product = self.env['product.product'].browse(id_product)
        lst_poduct_details.append(product[0]['name'])
        lst_poduct_details.append(product[0]['standard_price'])
        lst_poduct_details.append(product[0]['qty_available'])
        return lst_poduct_details

    def get_report(self,start_date,end_date):

        tbl_stock_move_line_by_date = self.Get_stock_move_line_by_date(start_date,end_date)
        dataframe = pd.DataFrame(pd.DataFrame(tbl_stock_move_line_by_date, columns=[
            'product_id', 'qty_done']).groupby('product_id').agg({'qty_done': sum}, columns=[
                'product_id', 'qty_done']))

        lst_product_id = dataframe.index.tolist()
        lst_qty_done = dataframe.values.tolist()
        lst_product_detailed = []
        if len(lst_product_id) == len(lst_qty_done):
            for i in range(len(lst_product_id)):
                product = self.Get_product_template(lst_product_id[i])
                product_detailed = lst_product_id[i], product[0], lst_qty_done[i][0], product[1], product[2]            
                lst_product_detailed.append(product_detailed)
        dataframe = pd.DataFrame(lst_product_detailed, columns=[
                                 'Id Producto', 'Producto', 'Cantidad Vendida', 'Precio de Compra', 'Cantidad en Stock'])
        dataframe['Costo'] = ((dataframe['Precio de Compra']) *
                              (dataframe['Cantidad en Stock']))
        dataframe['Promedio'] = ((dataframe['Cantidad Vendida'])/3)
        dataframe['Cantidad de Exceso de Inventario'] = (
            (dataframe['Cantidad en Stock'])-dataframe['Promedio'])
        dataframe = dataframe.drop(dataframe[dataframe['Cantidad de Exceso de Inventario']<=0].index)
        towrite = io.BytesIO()
        dataframe.to_excel(towrite, index=False,columns=['Id Producto','Producto','Precio de Compra','Cantidad en Stock','Costo','Cantidad de Exceso de Inventario'])
        towrite.seek(0)
        return towrite
        


   






    