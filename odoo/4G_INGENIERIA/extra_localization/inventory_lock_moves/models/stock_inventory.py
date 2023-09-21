# -*- coding: utf-8 -*-
from odoo import models, fields, api

class stockinventory(models.Model):
    _inherit = "stock.inventory"
    
    motivo_de_ajuste = fields.Text(
        string='Motivo de Ajuste de inventario',
        required=True
        
    )
    
