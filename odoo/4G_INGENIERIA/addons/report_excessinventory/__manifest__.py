# -*- coding: utf-8 -*-

{
    'name' : 'Report of excessinventory',
    'version' : '1',
    'summary': 'Modulo de reportes de productos de exceso de inventario',
    'sequence': 30,
    'description': """
	this module is about reports of productos, how:
		- report excess of inventory

    """,
    'author': '4g-nina',
    'category' : 'product',
    'website': 'http://www.4gingenieria.com',
    'images' : [],
    'depends' : ['product'],
    'data': [
        'report_excessinventory.xml',
	'report/report_excessinventory_report.xml',
	'cambios_excess.xml',
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
