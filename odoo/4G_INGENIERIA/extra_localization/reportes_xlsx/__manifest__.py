# -*- coding: utf-8 -*-
{
    'name': "Report Back Order Excel Plugin",

    'summary': """
    Complemento al módulo de Back Order para realizar reporte en Excel
    """,

    'description': """
       Genera reporte personalizado de consultas SQL a excel a modelos de odoo.\n
       Para generar el reporte desde cualquier módulo se debe agregar un botón \n
       <button name="print_kardex_xlsx" type="object" string="Imprimir Reporte Excel"/>\n
       además del siguiente método :

       @api.multi
       def print_kardex_xlsx(self):
        return {'type': 'ir.actions.report','report_name': 'reportes_xlsx.report_back_order_xlsx','report_type':"xlsx"}

        en el modelo de la vista en la cuál se quiera implementar.
    """,

    'author': "José Roberto Mejía Pacheco",
    'website': "https://github.com/isscjrmpacheco",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Desarrollos 4G',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/report.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application':False,
    'installable':True,
    'autoninstall':True


}