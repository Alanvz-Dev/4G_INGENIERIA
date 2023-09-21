from odoo import models,api

class PartnerXlsx(models.AbstractModel):
    _name = 'report.reportes_xlsx.report_back_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('sahjdsaj')
        
        columns = ["Fecha", "No. Pedido", "Cliente", "Descripcion","Precio","Cantidad Pedida","Back Order","Total","Status"]
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
        self.env.cr.execute("SELECT so.date_from_lead, so.name,rp.name,sl.name,sl.price_unit, sl.product_uom_qty, sl.product_uom_qty-sl.qty_invoiced, sl.price_unit*(sl.product_uom_qty-sl.qty_invoiced), so.state FROM sale_order so JOIN sale_order_line sl ON so.id=sl.order_id JOIN product_product pp ON pp.id=sl.product_id JOIN res_partner rp on rp.id=so.partner_id WHERE date_from_lead BETWEEN '2018-01-01' AND current_date AND sl.product_uom_qty > sl.qty_invoiced AND so.state !='cancel' AND so.state !='draft' AND so.state !='sent';")
        report_details = self.env.cr.fetchall()
        report_array = []
        for valores in report_details:
            report_array.append(valores)
        print(report_array)    
        return report_array