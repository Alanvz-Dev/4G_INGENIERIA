# -*- coding: utf-8 -*-

{
    'name' : 'Envio de Ordenes de Compra',
    'version' : '1',
    'summary': 'Modulo para el desarrollo de productos en orden de compra',
    'sequence': 30,
    'description': """

    Modulo que acutaliza los precios de los productos en tiempo real dependiendo su categoría

    """,
    'author': '4G',
    'category' : 'Customizaciones',
    'website': 'http://www.4gingenieria.om',
    'images' : [],
    'depends' : ['product','purchase','base','sale',"account"],
    'data': [
        #'costos_productos.xml',
        #'purchaseorder_costos.xml',

    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}