# -*- coding: utf-8 -*-

{
    'name' : 'Escenario de Ventas Fecha desde flujo de ventas',
    'version' : '1',
    'summary': 'Modulo para traer fecha de flujo de ventas',
    'sequence': 30,
    'description': """

    Este modulo realiza una monitorizacion al escenario de ventas

    """,
    'author': '4g',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.om',
    'images' : [],
    'depends' : ['sale_crm'],
    'data': [
        'views/inherit_sale_order_view.xml',

    ],
    'demo': [

    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
