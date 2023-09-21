# -*- coding: utf-8 -*-

{
    'name' : 'Actualizacion de Factura',
    'version' : '1',
    'summary': 'Modulo para modificar facturas',
    'sequence': 30,
    'description': """

    Modulo para realizar actualizaciones en las facturas

    """,
    'author': '4g',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.com',
    'images' : [],
    'depends' : ['product','purchase'],
    'data': [
        'account_invoice.xml',
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}