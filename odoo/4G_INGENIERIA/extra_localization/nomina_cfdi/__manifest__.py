# -*- coding: utf-8 -*-

{
    'name': 'Nomina Electrónica para México CFDI v1.2',
    'summary': 'Agrega funcionalidades para timbrar la nómina electrónica en México.',
    'description': '''
    Nomina CFDI Module
    ''',
    'author': 'IT Admin',
    'version': '11.17',
    'category': 'Employees',
    'depends': [
        'hr_payroll', 'cdfi_invoice','hr_payroll_account','mrp'
    ],
    'data': [
        'data/sequence_data.xml',
        'data/cron.xml',
        'data/nomina.otropago.csv',
        'data/nomina.percepcion.csv',
        'data/nomina.deduccion.csv',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_salary_view.xml',
        'views/hr_payroll_payslip_view.xml',
        'views/tablas_cfdi_view.xml',
        'views/res_company_view.xml',
        'report/report_payslip.xml',
        'views/res_bank_view.xml',
        'data/mail_template_data.xml',
        'security/ir.model.access.csv',
        'data/res.bank.csv',
        'views/menu.xml',
        'views/horas_extras_view.xml',
        'wizard/wizard_liquidacion_view.xml',
        'wizard/import_nomina_xml.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}
