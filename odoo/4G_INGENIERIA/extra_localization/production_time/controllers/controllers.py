# -*- coding: utf-8 -*-
from odoo import http

class ProductionTime(http.Controller):
#     @http.route('/production_time/production_time/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/production_time/production_time/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('production_time.listing', {
#             'root': '/production_time/production_time',
#             'objects': http.request.env['production_time.production_time'].search([]),
#         })

#     @http.route('/production_time/production_time/objects/<model("production_time.production_time"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('production_time.object', {
#             'object': obj
#         })

     @http.route('/graph/<self_id>', auth='public', website=True)
     def graph(self,self_id):
      return http.request.render('production_time.graph_template', {
       'x_axis':[1500,1600,1700,1750,1800,1850,1900,1950,1999,2050],
       'y_axis':[86,114,106,106,107,111,133,221,783,2478],
       }) 