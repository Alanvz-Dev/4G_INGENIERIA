# -*- coding: utf-8 -*-
{
    'name': "4g Attendance",
    'version': "1.0.4",
    'author': "IT Admin",
    'category': "",
    'depends': ['hr_attendance','hr_payroll', 'nomina_cfdi', 'web_tree_dynamic_colored_field'],
    'data': [
            'security/ir.model.access.csv',
            'templates/assets.xml',
            'wizard/import_attendance_view.xml',
            'wizard/remain_import_attandance.xml',
            'views/reporte_asistencia_view.xml',
            'data/if_roll_number.xml',    
            'views/hr_payrol_run.xml',
    ],
    'installable': True,
}
