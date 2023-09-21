# -*- coding: utf-8 -*-
{
    'name': "flujo_efectivo",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'escenario_de_ventas'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/flujo_efectivo_flujo_efectivo.xml',
        'views/flujo_efectivo_flujo_efectivo_config.xml',
        'views/flujo_efectivo_pivot_button_template.xml',
        'views/flujo_efectivo_credit_line.xml',
        'views/flujo_efectivo_balance_bank.xml',
        'wizard/flujo_efectivo_agregar_monto.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        # 'static/src/js/xml/button.xml'
    ]
}
