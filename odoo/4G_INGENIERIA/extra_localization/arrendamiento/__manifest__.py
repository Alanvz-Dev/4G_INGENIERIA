# -*- coding: utf-8 -*-
{
    'name': "Arrendamientos",

    'summary': """
        Modulo de prueba""",

    'description': """
        Modulo de prueba para arrenadamientos 4g
    """,

    'author': "4G ingeniería",
    'website': "http://odoo.4gingenieria.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/account_asset_asset.xml',
        'views/views_vehicle.xml',
        'views/views_machine.xml',
        'views/menu.xml', 
        'views/account_invoice.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}