# -*- coding: utf-8 -*-
{
    'name': "Nómina 4G",

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
    'depends': ['base','hr_holidays','hr','calendar','hr_payroll', 'resource'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',        
        'views/nomina_semanal/detalle_nomina_semanal.xml',      
        'views/detalle_horas_de_trabajo.xml',
        'views/detalle_horas_de_trabajo_nomina.xml',
        'views/search_view_holidays.xml',
        'views/search_view_horas_de_trabajo.xml',
        'views/horas_extra/balance_de_dias_laborados.xml',
        'views/horas_extra/historial_de_dias_laborados.xml',
        'views/horas_extra/horas_extra.xml',
        'views/empleados_administrativos/empleados_administrativos.xml',
        'views/menu.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}