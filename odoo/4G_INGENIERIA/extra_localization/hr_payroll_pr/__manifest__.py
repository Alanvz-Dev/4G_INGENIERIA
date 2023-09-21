# -*- coding: utf-8 -*-
{
    'name': "Nómina 4G 2.0",

    'summary': """
        Empleados, Horas Trabajadas, Faltas, Incidencias...
        """,

    'description': """
        Administración de Avisos Múltiples, Mayordomías, Tiempo extra , fuera de horario  u horario irregular.
        Integrado con Nómina CDFDI.
    """,

    'author': "José Roberto Mejía Pacheco",
    'website': "http://www.isscjrmpacheco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Nómina',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['hr','mrp','calendar','hr_payroll','nomina_cfdi','web_progress'],
    # always loaded
    'data': [
        'views/hr_view_employee_form.xml',
        'views/hr_payroll_pr_in_out.xml',
        'views/hr_payroll_pr_mayordomia.xml',
        'views/empleados_administrativos.xml',
        'views/hr_payroll_pr_mayordomia_line.xml',
        'views/hr_payroll_pr_incidencias_bonos_configuracion.xml',
        'wizard/hr_payroll_pr_asignar_proyecto.xml',
        'views/hr_payroll_pr_turno.xml',        
        'views/hr_payroll_pr_horas_proyecto.xml',
        'views/hr_payroll_pr_resumen_nomina_line.xml',
        'views/hr_payroll_pr_resumen_nomina.xml',
        'wizard/hr_payslip_run.xml',
        'wizard/hr_payroll_pr_asignar_horas_a_pagar.xml',
        'views/res_partner_bank.xml',
        'views/menu.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}