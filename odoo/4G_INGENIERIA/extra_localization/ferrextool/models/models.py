# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime 
from dateutil.relativedelta import relativedelta
import numpy as np
class ferrextool_reports(models.Model):
    _name = 'ferrextool.reports'
    

    report_type=fields.Selection([ ('slow', 'Lento Movimiento'),('excess', 'Exceso de Inventario'),],'Tipo de Reporte')
    start_date = fields.Date(required='true')
    end_date = fields.Date(required='true')

    def button_download_contract(self):
        return self.env.ref('ferrextool.slow_excess').report_action(self, data={}, config=False)



class SlowEcxessXlsxReport(models.AbstractModel):
    #_name = 'report.module_name.report_name'
    _name = 'report.ferrextool.slow_excess_report'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, partners):
        fecha_incial=partners.start_date
        fecha_final=partners.end_date
        date_fecha_inicial= datetime.strptime(fecha_incial, '%Y-%m-%d')
        date_fecha_final= datetime.strptime(fecha_final, '%Y-%m-%d')
        meses=date_fecha_final - date_fecha_inicial
        meses=str(meses)
        print(meses[0]+meses[1]+meses[2])
        mes_rango=int(meses[0]+meses[1]+meses[2])/30
        print(mes_rango/30)
        exceso=[]
        products=self.env['product.product']
        cr = self._cr
        queryy="select  sml.product_id ,sum(sml.qty_done)/"+str(mes_rango)+" suma from stock_move_line sml where sml.reference like '%GRAL/OUT/%' and state in ('done') and sml.create_date >'"+fecha_incial+"' and sml.create_date <'"+fecha_final+"' group by sml.product_id"
        cr.execute(queryy)
        prod_ids=[]
        products_array = cr.fetchall()
        for product in products_array:
            current_product=products.browse(product[0])
            if current_product.qty_available >product[1]:
                prod_ids.append(current_product.id)
                exceso.append({
                'product_id':current_product.product_tmpl_id.id,
                'name':current_product.name,
                'reference':current_product.default_code,
                'qty_available':current_product.qty_available,
                'qty_excess':current_product.qty_available - product[1],
                'unit_price':current_product.standard_price,
                'total':float((current_product.qty_available - product[1])*current_product.standard_price),
                })

        if partners.report_type=='excess':
            sheet = workbook.add_worksheet('Ecxeso de Inventario FERREXTOOL')
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, 'Id Producto', bold)
            sheet.write(0, 1, 'Referencia', bold)
            sheet.write(0, 2, 'Nombre', bold)
            sheet.write(0, 3,'Cantidad Disponible', bold)
            sheet.write(0, 4, 'Exceso', bold)
            sheet.write(0, 5, 'Costo', bold)
            sheet.write(0, 7, 'Total', bold)
            for item in range(len(exceso)):
                sheet.write(item+1, 0, exceso[item].get('product_id'))
                sheet.write(item+1, 1, exceso[item].get('reference'))
                sheet.write(item+1, 2, exceso[item].get('name'))
                sheet.write(item+1, 3, exceso[item].get('qty_available'))
                sheet.write(item+1, 4, exceso[item].get('qty_excess'), bold)
                sheet.write(item+1, 5, exceso[item].get('unit_price'))
                sheet.write(item+1, 6, exceso[item].get('total'))


        if partners.report_type=='slow':
            lento=[]

            start_date = datetime.now()
            end_date = datetime.now() - relativedelta(months=3) 
            print(start_date.strftime("%Y-%m-%d"))
            print(end_date.strftime("%Y-%m-%d"))

            list_stock_move_line_con_venta= self.env['stock.move.line'].search([
                ('reference','ilike','GRAL/OUT/'),
                ('product_id','not in',prod_ids),
                ('state','in',['done']),
                ('create_date','>',fecha_incial),
            #end_date.strftime("%Y-%m-%d")
            ('create_date','<',fecha_final)       
            ]).mapped('product_id').ids

            list2=np.append(list_stock_move_line_con_venta,prod_ids).tolist()
            list3=list(set(list2)) 

            list_stock_move_line_sin_ventas= self.env['stock.move.line'].search([
                ('reference','not ilike','GRAL/OUT/'),
                ('product_id','not in',list3),
                ('state','in',['done']),
            ('create_date','>',fecha_incial),#end_date.strftime("%Y-%m-%d")
            ('create_date','<',fecha_final)       
            ]).mapped('product_id').ids


            list_stock_move_line = list(set(list_stock_move_line_sin_ventas)) 

            products=self.env['product.product'].search([('id','in',list_stock_move_line)])
            for product in products:
                if product.qty_available >0:
                    lento.append({
                    'qty_available':product.qty_available,
                    'id':product.product_tmpl_id.id,
                    'reference':product.default_code,
                    'name':product.name,
                    'unit_price':product.standard_price,
                    'total':float(product.qty_available*product.standard_price)
                    })

            sheet = workbook.add_worksheet('Lento Movimiento FERREXTOOL')
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, 'Id Producto', bold)
            sheet.write(0, 1, 'Referencia', bold)
            sheet.write(0, 2, 'Nombre', bold)
            sheet.write(0, 3,'Cantidad Disponible', bold)
            sheet.write(0, 4, 'Costo', bold)
            sheet.write(0, 5, 'Total', bold)
            for item in range(len(lento)):
                sheet.write(item+1, 0, lento[item].get('id'))
                sheet.write(item+1, 1, lento[item].get('reference'))
                sheet.write(item+1, 2, lento[item].get('name'))
                sheet.write(item+1, 3, lento[item].get('qty_available'),bold)
                sheet.write(item+1, 4, lento[item].get('unit_price'))
                sheet.write(item+1, 5, lento[item].get('total'))




