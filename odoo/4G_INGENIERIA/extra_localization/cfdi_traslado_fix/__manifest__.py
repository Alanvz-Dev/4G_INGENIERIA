# -*- coding: utf-8 -*-
{
    'name': "cfdi_traslado_fix",

    'summary': """
Solución al error causado por el módulo cfdi_traslado
""",

    'description': """
       Solución temporal al error:

  File "/opt/odoo/odoo/odoo/models.py", line 2763, in _read_from_database
    cr.execute(query_str, params)
  File "/opt/odoo/odoo/odoo/sql_db.py", line 155, in wrapper
    return f(self, *args, **kwargs)
  File "/opt/odoo/odoo/odoo/sql_db.py", line 232, in execute
    res = self._obj.execute(query, params)
psycopg2.errors.UndefinedColumn: column res_partner.cce_licencia does not exist
LINE 1: ...play_name","res_partner"."function" as "function","res_partn...

    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}