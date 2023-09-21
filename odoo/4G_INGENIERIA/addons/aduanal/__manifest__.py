# -*- coding: utf-8 -*-
##############################################################################
#                 @author IT Admin
#
##############################################################################

{
    'name': 'Aduanal CFDI 3.3',
    'version': '11.3',
    'description': ''' Agrega información de pedimentos al CFDI 3.3
    ''',
    'category': 'Accounting', 'Sales'
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'base','sale', 'cdfi_invoice', 'sale_order_lot_selection',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_lot_view.xml',
        'report/invoice_report.xml',
    ],
    'application': False,
    'installable': True,
}
