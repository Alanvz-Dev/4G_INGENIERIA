# -*- coding: utf-8 -*-

{
    'name' : 'Escenario de Ventas',
    'version' : '1',
    'summary': 'Modulo para consulta de ventas',
    'sequence': 30,
    'description': """

    Este modulo realiza una monitorizacion al escenario de ventas

    """,
    'author': '4g',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.om',
    'images' : [],
    'depends' : ['sale','product', 'sale_order_date_from_lead'],
    'data': [

    ],
    'demo': [

    ],
    'qweb': ['static/src/xml/*.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
