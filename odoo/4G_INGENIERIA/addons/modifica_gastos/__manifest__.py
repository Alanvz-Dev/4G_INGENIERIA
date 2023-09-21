# -*- coding: utf-8 -*-

{
    'name' : 'Actualizacion de Gastos',
    'version' : '1',
    'summary': 'Modulo para modificar gastos',
    'sequence': 30,
    'description': """

    Modulo para realizar actualizaciones en los gastos

    """,
    'author': '4g',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.com',
    'images' : [],
    'depends' : ['product','purchase'],
    'data': [
        'hr_expenses_view.xml',
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}