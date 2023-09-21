# -*- coding: utf-8 -*-
{
    'name': "complemento_leyenda_ext",

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
    'depends': ['4g_invoice_report','complemento_leyenda'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/complemento_leyenda_ext_tax_legend.xml',
        'views/account_invoice.xml',     
        'report/4g_invoice_report.xml',   
        'views/res_company.xml',
        'views/complemento_leyenda_ext_menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}