# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CveClaveUnidad(models.Model):
    _name = 'cfdi_traslado_ext.catalogo_colonia'
    _rec_name = "c_localidad"
    c_codigoPostal = fields.Char(string='Clave Código Postal')
    c_estado = fields.Char(string='Clave Estado')
    c_municipio = fields.Char(string='Clave Municipio')
    c_localidad = fields.Char(string='Clave Localidad')


# id,c_codigoPostal,c_estado,c_municipio,c_localidad
# cfdi_traslado_ext_catalogo_colonia1,"0","AGU","0","100"
# cfdi_traslado_ext_catalogo_colonia2,"20000","AGU","1","200"



# # -*- coding: utf-8 -*-

# from odoo import models, fields, api

# class CveClaveUnidad(models.Model):
#     _name = 'catalogos.x'
#     _rec_name = "c_localidad"
#     c_codigoPostal = fields.Char(string='Clave Código Postal')
#     c_estado = fields.Char(string='Clave Estado')
#     c_municipio = fields.Char(string='Clave Municipio')
#     c_localidad = fields.Char(string='Clave Localidad')