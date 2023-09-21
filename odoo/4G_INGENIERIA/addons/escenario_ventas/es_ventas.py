# -*- coding: utf-8 -*-

from odoo import models,fields,api,_


class sale_order(models.Model):
	_name='sale.order'
	_inherit='sale.order'
	_description='Escenario de Ventas'
	no_compra_cliente=fields.Char('Orden de compra - Cliente',required=True)
  
class account_invoice(models.Model):
	_name='account.invoice'
	_inherit='account.invoice'
	_description='Escenario de Ventas en facturacion'
	no_compra_cliente = fields.Boolean(related="sale_order.no_compra_cliente")