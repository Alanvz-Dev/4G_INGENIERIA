# -*- coding: utf-8 -*-
{
    'name': "4g_production",

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
    'depends': ['base','mrp','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_work_center.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/product_template.xml',
        'views/mrp_bom.xml',
        'views/mrp_routing_views.xml',
        'views/capacidad_de_produccion_grafica_dia.xml',
        'views/capacidad_de_produccion_grafica.xml',
        'views/capacidad_de_produccion_grafica_menu.xml',
        'views/mrp_workorder_views.xml',
        'views/capacidad_de_produccion_calibres.xml',
        'views/capacidad_de_produccion_calibres_menu.xml',
        'wizard/reporte_diario_de_produccion/view_reporte_diario_de_produccion.xml',
        'views/stock_move_picking_list.xml',
        'views/mrp_production.xml',
        'views/mrp_picking_list.xml',
        'views/mrp_picking_list_summary.xml',
        'views/mrp_picking_list_settings.xml'
        # 'wizard/reporte_diario_de_produccion/mrp_reporte_diario_de_produccion_list.xml'
        #prduct.product
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}