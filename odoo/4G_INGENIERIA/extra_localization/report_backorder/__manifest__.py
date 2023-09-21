# -*- coding: utf-8 -*-

{
    'name' : 'Report of backorder',
    'version' : '1',
    'summary': 'Modulo de reportes de productos',
    'sequence': 30,
    'description': """
	this module is about reports of productos, how:
		- report back order

    """,
    'author': '4g-nina',
    'category' : 'product',
    'website': 'http://www.4gingenieria.com',
    'images' : [],
    'depends' : ['product'],
    'data': [
        'report_backorder.xml',
	    'report/report_backorder_report.xml',
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
