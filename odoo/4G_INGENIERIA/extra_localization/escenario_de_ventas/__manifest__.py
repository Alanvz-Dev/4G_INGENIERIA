# -*- coding: utf-8 -*-
{
    'name': "Escenario de Ventas",

    'summary': """
        Rr""",

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
    'depends': ['base','crm','mrp','mail','product','sale_crm'],

    # always loadedS
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/escenario_de_ventas_hoja_de_proyecto_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/escenario_de_ventas_views_menu.xml',
        'views/escenario_de_ventas_flujo_de_efectivo.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

