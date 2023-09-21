from xmlrpc.client import ServerProxy
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from time import time
import io
def Get_stock_move_line_by_date(start_date,end_date):
    return self.env['stock.move.line'].search(
        [
            [('state', '=', 'done'),
             ('location_dest_id', '=', 9),
                ('date', '>=',start_date),
                ('date', '<=', end_date)
             ],
            [
                'product_id',
                'qty_done',
            ]
        ]
    )



def Get_product_template(id_product):
    product = self.env['product.product'].search(
        [
            ["|",
             ["active", "=", True],
             ["active", "=", False], ('id', '=', id_product)],
            [
                'name',
                'standard_price',
                'qty_available'
            ]
        ])
    lst_poduct_details.append(product[0]['name'])
    lst_poduct_details.append(product[0]['standard_price'])
    lst_poduct_details.append(product[0]['qty_available'])
    return lst_poduct_details
def get_report(start_date,end_date):
    tbl_stock_move_line_by_date = Get_stock_move_line_by_date(start_date,end_date)
    lst_id_qty_done = []
    for item in tbl_stock_move_line_by_date:
        prod = (item['product_id'][0], item['qty_done'])
        lst_id_qty_done.append(prod)
    dataframe = pd.DataFrame(pd.DataFrame(lst_id_qty_done, columns=[
        'product_id', 'qty_done']).groupby('product_id').agg({'qty_done': sum}, columns=[
            'product_id', 'qty_done']))

    lst_product_id = dataframe.index.tolist()
    lst_qty_done = dataframe.values.tolist()
    lst_product_detailed = []
    if len(lst_product_id) == len(lst_qty_done):
        for i in range(len(lst_product_id)):
            product = Get_product_template(lst_product_id[i])
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



Si no mueves los productos en 3 meses
no esta moviendo y los tengo alli