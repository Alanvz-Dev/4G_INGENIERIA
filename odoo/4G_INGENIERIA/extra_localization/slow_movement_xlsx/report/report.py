import pickle
from odoo import models,api
class PartnerXlsx(models.Model):
    _name = 'report.slow_movement_xlsx.report_slow_movement_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('sahjdsaj')
        
        columns = ["Nombre", "Suma", "Precio", "Total"]
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
        start_date = pickle.load(read)
        read.close()
        print(start_date)
        read2 = open('/globales/global_end_date', 'rb')
        end_date = pickle.load(read2)
        read2.close()
        print(end_date)
        sql_query="select pp.name,(select sum(sq.quantity) from stock_quant sq  join stock_location sl on sl.id=sq.location_id where pp.id=sq.product_id and sl.usage='internal'and in_date between  ' "+str(start_date)+" '  and  ' "+str(end_date)+" '),pp.list_price, (select sum(sq.quantity) from stock_quant sq  join stock_location sl on sl.id=sq.location_id  where pp.id=sq.product_id and sl.usage='internal' and in_date between ' "+str(start_date)+" ' and ' "+str(end_date)+" ') *pp.list_price as total from product_template pp WHERE pp.id NOT IN (select product_id from purchase_order_line where date_planned between ' "+str(start_date)+" ' and ' "+str(end_date)+" ') And pp.id NOT IN (select sl.product_id from sale_order_line sl join sale_order so on sl.order_id=so.id  where so.date_from_lead  between ' "+str(start_date)+" ' and ' "+str(end_date)+" ') and (select sum(sq.quantity) from stock_quant sq  join stock_location sl on sl.id=sq.location_id where pp.id=sq.product_id and sl.usage='internal' and in_date between ' "+str(start_date)+" ' and ' "+str(end_date)+" ') >0 group by pp.id, pp.name,pp.list_price"
        print(sql_query)
        self.env.cr.execute(sql_query)
        report_details = self.env.cr.fetchall()
        report_array = []
        for valores in report_details:
            report_array.append(valores)
        print(report_array)    
        return report_array