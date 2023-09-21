# -*- coding: utf-8 -*-
##############################################################################
#                 @author IT Admin
#
##############################################################################

{
    'name': 'Complemento Leyenda CFDI',
    'version': '11.01',
    'description': ''' Agrega información de Leyendas al CFDI
    ''',
    'category': 'Accounting', 'Sales'
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'base', 'account', 'cdfi_invoice'
    ],
    'data': [
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',
        'report/invoice_report.xml',
    ],
    'application': False,
    'installable': True,
}
