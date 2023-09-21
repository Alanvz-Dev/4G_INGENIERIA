# -*- coding: utf-8 -*-
{
    'name': "Bloqueo de Movimientos Contables",

    'summary': """
        Bloquea la creación de pólizas (Movimientos)""",

    'description': """
        Al momento de instalar el módulo si no se tienen registrados periodos abiertos,
        no le permitirá realizar ningún movimiento ya que cualquier fecha no registrada en el módulo
        seconsidera como cerrada para evitar afectación en la contabilidad de los meses cerrados.
    """,

    'author': "José Roberto Mejía Pacheco",
    'website': "https://www.facebook.com/isscjrmp/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/wizard_lock_account_moves.xml',
        'views/views.xml',
        'views/templates.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}