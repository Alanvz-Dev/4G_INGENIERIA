# -*- coding: utf-8 -*-
{
    'name': "nomina_cfdi_ext",

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
    'depends': ['hr_payroll','nomina_cfdi','web_progress','nomina_cfdi_extras','hr','hr_payroll_account'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        
        'views/hr_payslip_run.xml',
        'views/nomina_cfdi.message.xml',
        # 'wizard/modify_slip.xml' ,
        'views/hr_payslip.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}