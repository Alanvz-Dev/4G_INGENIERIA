# -*- coding: utf-8 -*-

{
    'name' : 'Actualizacion de  fabricacion',
    'version' : '1',
    'summary': 'Modulo para actualizacion de fabricacion',
    'sequence': 30,
    'description': """

    Modulo para realizar actualizaciones en la orden de manufactura, crea dos campos para ingresar quien recibio y entrego la MO

    """,
    'author': '4g',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.com',
    'images' : [],
    'depends' : ['product','purchase'],
    'data': [
        'mrp_production.xml',
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}