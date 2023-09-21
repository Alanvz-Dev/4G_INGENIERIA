# -*- coding: utf-8 -*-
{
    'name': "production_time",

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
    'depends': ['mrp','web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/production_time_production_time.xml',
        'views/production_time_work_center_config.xml',
        'views/production_time_wizard.xml',
        'views/production_time_data.xml',
        'views/production_time_graph.xml',
        'views/custom_widget.xml',
        
    ],
    'qweb': [
        'views/custom_widget_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
