from odoo import _, api, fields, models


class TaxLegends(models.Model):
    _name = 'complemento_leyenda_ext.tax_legend'
    _description = 'Leyendas Fiscales'

    name = fields.Char(string='Nombre',help='Este dato sirve para identificarlo, no afecta en el timbrado')
    tax_provision = fields.Char(string='Disposición Fiscal')
    rule = fields.Char(string='Norma')
    legend = fields.Text(string='Leyenda')
