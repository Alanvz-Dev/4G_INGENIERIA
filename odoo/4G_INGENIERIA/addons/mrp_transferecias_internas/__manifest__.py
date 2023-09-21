# -*- coding: utf-8 -*-
{
    'name': "mrp_transferencias_internas",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """ Este modulo permite incorporar Solicitudes de Material de forma interna en Produccion.

Se Desarrollo un Boton llamado Solicitud de Transferencia en Produccion el cual permite Solicitar de Ubicaciones internas la Materia Prima.

Configuracion
=============

Debemos crear o Marcar una Operación para la consulta de las Ubicaciones Inventario --> Todas las Operaciones --> Campo Para Abastecimiento de Produccion 

Notas:
    * Si en la Ubicacion Origen existen Cantidades Negativas el Sistema Sumara la Cantidad Negativa mas la requerida para tener el Material Necesario.
""",

    'author': "4G Ingeniería",
    'website': "https://github.com/isscjrmpacheco",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Desarollos4gIngenieria',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['mrp_purchase_integration',
        'mrp',
        'purchase',
        'account_accountant',
        'stock_account',
        'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True
}