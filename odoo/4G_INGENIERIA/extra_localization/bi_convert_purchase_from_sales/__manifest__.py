# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name' : "Convert Purchase from Sales Order",
    'version' : "11.0.0.3",
    'author' : "BrowseInfo",
    'summary': 'This apps helps to Covert Purchase order from Sales Order',
    'description' : """
        Convert Purchase from Sales Order
        Convert Purchases from Sales Order
        Convert Purchase order from Sales Order
        Convert Purchases order from Sales Order

        create Purchase from Sales Order
        create Purchases from Sales Order
        create Purchase order from Sales Order
        create Purchases order from Sales Order


        Add Purchase from Sales Order
        Add Purchases from Sales Order
        ADD Purchase order from Sales Order
        ADD Purchases order from Sales Order

     """,
    'category' : "Purchases",
    'website'  : "https://www.browseinfo.in",
    'depends'  : [ 'base','sale_management','purchase'],
    'data'     : [
                'wizard/purchase_order_wizard_view.xml',
                'views/inherit_sale_order_view.xml',
            ],      
    'test' :  [ ],
    'css'  :  [ ],
    'demo' :  [ ],
    'installable' : True,
    'application' :  False,
    "images":['static/description/Banner.png'],
    'live_test_url':'https://youtu.be/wS4f9hEABxY',
}
