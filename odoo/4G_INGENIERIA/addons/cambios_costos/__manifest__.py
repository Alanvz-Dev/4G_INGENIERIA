# -*- coding: utf-8 -*-

{
    'name' : 'Actualizacion de costos productos',
    'version' : '1',
    'summary': 'Modulo para el desarrollo de productos',
    'sequence': 30,
    'description': """

    Modulo para realizar actualizaciones en los costos de los productos, dependiendo de la categoria

    """,
    'author': '4g',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.com',
    'images' : [],
    'depends' : ['product','purchase'],
    'data': [
        'costos_productos.xml',
        'template_accountinvoice_report.xml',
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