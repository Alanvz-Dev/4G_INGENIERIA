# -*- coding: utf-8 -*-
# © 2014 Today Akretion (http://www.akretion.com).
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Solicitudes de Presupuesto desde Órdenes de producción',
    'version': '10.1',
    'category': 'MRP',
    'author': 'José Roberto Mejía Pacheco',
    'website': 'https://www.linkedin.com/in/jrmpacheco/',
    'license': 'AGPL-3',
    'description': """




    """,
    'depends': [
        'stock_available_unreserved',
        'mrp',
        'purchase',
        'account_accountant',
        'stock_account',
        'stock',
    ],
    'data': [
        
        'views/product_template.xml',
        'wizard/asistente_material_required.xml',
        'views/mrp_production.xml',
    ],
    'installable': True,
}


