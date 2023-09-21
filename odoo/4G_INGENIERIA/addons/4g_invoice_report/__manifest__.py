# -*- coding: utf-8 -*-
##############################################################################
#                 @author Duvan Zavaleta
#
##############################################################################

{
    'name': 'Custom 4g Invoice Format',
    'version': '11.1',
    'description': ''' Pagos y facturas
    ''',
    'category': 'Accounting',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'base',
        'account','account_invoicing','cdfi_invoice',
    ],
    'data': [
        'report/invoice_report_custom.xml',
       'views/sale_view.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
    'price': 0.00,
    'currency': 'USD',
    'license': 'OPL-1',	
}
