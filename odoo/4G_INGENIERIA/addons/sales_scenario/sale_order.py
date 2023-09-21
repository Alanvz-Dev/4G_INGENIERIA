# -*- coding: utf-8 -*-


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    no_compra = fields.Char(string='Orden de compra - Cliente')
    probability = fields.Selection([('high','Alta Probabilidad'),('low','Alta Probabilidad / Orden de Compra'),],'Probabilidad de proyecto')


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    piezas_limite = fields.Char('Limite de Piezas')
    
    
    
class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    apoyo = fields.Boolean('Costo especial')
    categoria_costo = fields.Many2one('categorycost.product','Nombre del producto')
    cost_category = fields.Float('Costo temporal',digits=(14,2))
    cuenta_analitica = fields.Many2one('account.analytic.account','Cuenta Analitica / Proyecto', no_create=True)
    autorizacion_compras = fields.Boolean('Liberada por Compras')
    pendiente_envio = fields.Boolean('Pendiente Envio OC',readonly=True)
    
    
class account_invoice(models.Model):
    _inherit= "account.invoice"
    
    no_compra_cliente = fields.Char(computed="sale_order.no_compra")    