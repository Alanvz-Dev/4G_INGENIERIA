# -*- coding: utf-8 -*-

{
    'name' : 'Actualizacion de costos en tiempo real de los productos',
    'version' : '1',
    'summary': 'Modulo para el desarrollo de productos en orden de compra',
    'sequence': 30,
    'description': """

    Modulo que acutaliza los precios de los productos en tiempo real dependiendo su caterogira

    """,
    'author': '4g',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.om',
    'images' : [],
    'depends' : ['product','purchase','base','sale',"account"],
    'data': [
        'purchaseorder_costos.xml',
        'report/ev_proveedores_rerporte.xml',
        'report/report_materials_by_proyect.xml',

    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}