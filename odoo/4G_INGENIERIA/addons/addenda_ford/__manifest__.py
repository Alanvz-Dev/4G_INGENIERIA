# -*- coding: utf-8 -*-
##############################################################################
#                 @author IT Admin
#
##############################################################################

{
    'name': 'Addenda Ford',
    'version': '1.1',
    'description': ''' Agrega campos para generar la addenda de Ford
    ''',
    'category': 'Accounting',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'sale', 'cdfi_invoice',
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/res_company_view.xml',
        'views/sale_view.xml',
        #'report/invoice_report.xml',	
	],
    'application': False,
    'installable': True,
}
