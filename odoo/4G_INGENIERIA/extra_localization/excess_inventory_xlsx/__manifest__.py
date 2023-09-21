# -*- coding: utf-8 -*-
{
    'name': "Reporte Ecxeso de Inventario",

    'summary': """
    Complemento al módulo de excess_inventory_xlsx para realizar reporte en Excel
    """,

    'description': """
       Genera reporte personalizado de consultas SQL a excel a modelos de odoo.\n
       Para generar el reporte desde cualquier módulo se debe agregar un botón \n
       <button name="print_kardex_xlsx" type="object" string="Imprimir Reporte Excel"/>\n
       además del siguiente método :

       @api.multi
       def print_kardex_xlsx(self):
        return {'type': 'ir.actions.report','report_name': 'excess_inventory_xlsx.report_excess_inventory_xlsx','report_type':"xlsx"}

        en el modelo de la vista en la cuál se quiera implementar.

        Para guardar la fecha inicial se usa persistencia de datos con :
        read = open('global_start_date', 'rb')
        obj = pickle.load(read)
        read.close()
        print(obj)
        para generar el archivo donde se guardarán los valores, y para obtener los valores guardados se usa :
        
        read = open('global_start_date', 'rb')
        obj = pickle.load(read)
        read.close()
        print(obj)


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