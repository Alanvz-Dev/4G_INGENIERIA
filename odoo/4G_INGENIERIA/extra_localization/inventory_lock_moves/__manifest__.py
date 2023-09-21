# -*- coding: utf-8 -*-
{
    'name': "Bloqueo de Movimientos de Inventario",

    'summary': """
        Se crea un grupo para que unicamente una persona pueda realizar el ajuste de inventario""",

    'description': """
        Long description of module's purpose
    """,

    'author': "José Roberto Mejía Pacheco",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'views/stock_inventory.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        #'views/views.xml',
        'views/templates.xml',
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}