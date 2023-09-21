# -*- coding: utf-8 -*-

{
    'name' : 'Reporte ventas por cliente',
    'version' : '1',
    'summary': 'Modulo de reporte de ventas por cliente',
    'sequence': 30,
    'description': """
	reporte ventas por cliente
    """,
    'author': '4g-nina',
    'category' : 'product',
    'website': 'http://www.4gingenieria.com',
    'images' : [],
    'depends' : ['product'],
    'data': [
	'report_ventas.xml',
	'report/report_ventas_report.xml',
	'report/report_ventas_clientes.xml',
	'report/report_ventas_rutas.xml',

    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
