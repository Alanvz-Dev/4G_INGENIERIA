# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import re
import uuid
from collections import Counter, OrderedDict
from itertools import product
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError

class encuestas_mantenimiento(models.Model):
    """Calcula las url de todas las encuentas que contienen mantenimiento
    """

    _name = 'survey.maintenance'
    _description = 'Urls de Mantenimiento'
    #_rec_name = 'title'

    public_url_html_maintenance = fields.Char("Link")
    resultados = fields.Char("Resultados")
    nombre=fields.Char()
    encuestas_iniciadas=fields.Integer()
    encuestas_completadas=fields.Integer()

    @api.one
    @api.depends('nombre')
    def _compute_search_ids(self):
        print('View My Department CLO ACL')
        
    @api.multi
    def search_ids_search1(self,operator,operand):
        obj = self.env['survey.maintenance']
        obj.search([]).unlink()
        encuestas = self.env['survey.survey'].search([('title','ilike','mantenimiento'),('active','=',True)])
        for encuesta in encuestas:
            obj.create({'public_url_html_maintenance':encuesta.public_url,
            'nombre':encuesta.title,
            'encuestas_iniciadas':encuesta.tot_start_survey,
            'encuestas_completadas':encuesta.tot_comp_survey,
            'resultados':encuesta.result_url})

        
        obj = self.env['survey.maintenance'].search([]).ids 
        print(obj)       
        return [('id', 'in', obj)]


    search_ids = fields.Char(
        compute="_compute_search_ids", search='search_ids_search1')
 
