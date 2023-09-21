import pickle
from odoo import models,api
class PartnerXlsx(models.Model):
    _name = 'report.excess_inventory_xlsx.report_excess_inventory_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('sahjdsaj')
        
        columns = ["Nombre", "Precio", "Stock", "Suma"]
        for x in range(0,len(columns)):
            print (columns[x])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, x, columns[x], bold)

        lista=self.show_data_report_sale_order()
        print(type(lista))
        
        for rows in range(0,len(lista)):
            for columns in range(0,len(lista[rows])):
                print(lista[rows][columns])
                bold = workbook.add_format({'bold': False})
                sheet.write((rows+1), columns,lista[rows][columns], bold)
        cell_output='H'+str(len(lista)+2)
        formula='=SUM(H2:'+'H'+str(len(lista)+1)+")"
        sheet.write_formula(cell_output,formula)
        
    
    @api.multi
    def show_data_report_sale_order(self):
        read = open('/globales/global_start_date', 'rb')
        obj = pickle.load(read)
        read.close()
        print(obj)
        sql_query="select pp.name,pp.list_price, (select sum(sq.quantity) from stock_quant sq join stock_location sl on sl.id=sq.location_id where sl.usage='internal' and sq.in_date between  ' "+str(obj)+" ' and current_date and sq.product_id=pp.id) as stock, (select sum(sm.product_uom_qty) from stock_move sm  where pp.id=sm.product_id and sm.date between ' "+str(obj)+" ' and current_date and sm.location_dest_id=9) from product_template pp join stock_move sm on pp.id=sm.product_id join stock_quant sq on sq.product_id=pp.id where (select sum(sq.quantity) from stock_quant sq  join stock_location sl on sl.id=sq.location_id where sl.usage='internal' and sq.in_date between ' "+str(obj)+" ' and current_date and sq.product_id=pp.id) > (select sum(sm.product_uom_qty) from stock_move sm  where pp.id=sm.product_id and  sm.date between ' "+str(obj)+" ' and current_date and sm.location_dest_id=9) and sm.date between ' "+str(obj)+" ' and current_date group by pp.id,pp.list_price;"
        print(sql_query)
        self.env.cr.execute(sql_query)
        report_details = self.env.cr.fetchall()
        report_array = []
        for valores in report_details:
            report_array.append(valores)
        print(report_array)    
        return report_array