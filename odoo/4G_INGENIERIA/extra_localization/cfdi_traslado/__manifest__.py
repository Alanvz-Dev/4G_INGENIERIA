# -*- coding: utf-8 -*-
##############################################################################
#                 @author IT Admin
#
##############################################################################

{
    'name': 'CFDI Traslado',
    'version': '11.02',
    'description': ''' Agrega campos para generar CFDI de tipo traslado con el complemento de carta porte.
    ''',
    'category': 'Accounting',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'account', 'cdfi_invoice', 'catalogos_cfdi', 'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/invoice_report.xml',
        'views/factura_traslado_view.xml',
        'views/product_view.xml',
        'data/ir_sequence_data.xml',
        'views/res_partner_view.xml',
        'data/mail_template_data.xml',
        'views/stock_picking_view.xml',
        'views/autotransporte_view.xml',
	],
    'application': False,
    'installable': True,
}
