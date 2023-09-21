# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class arrendamiento(models.Model):
    _name = "arrendamiento.arrendamiento"
    active = fields.Boolean(default=True)
    # active_id = fields.Many2one("account.asset.asset", required=False)
    institucion = fields.Many2one("res.partner", required=False)
    dia_de_pago = fields.Integer(string="Día de pago", default=1, required=False)
    fecha_inicio = fields.Date(string="Fecha de inicio", required=False)
    fecha_vencimiento = fields.Date(string="Fecha de vencimiento", required=False)
    contrato = fields.Char(string="Contrato", required=False)
    invoice_ids = fields.Many2many("account.invoice", string="")
    invoice_count = fields.Char(compute="_compute_invoice_count", string="")
    invoice_balance = fields.Char(compute='_compute_invoice_balance', string='Saldo Actualizado')
    
    @api.multi
    def _compute_invoice_balance(self):
        for record in self:
            facturas_con_pago_amount = 0
            facturas_con_pago  = self.env["account.invoice"].search(
                [("id", "in", record.invoice_ids.ids),("state", "not in",['cancel','paid'])]
            )

            facturas_pagadas  = sum(self.env["account.invoice"].search(
                [("id", "in",  record.invoice_ids.ids),("state", "in",['paid'])]
            ).mapped('amount_total'))

            for item in facturas_con_pago:
                if item.residual !=0:
                    facturas_con_pago_amount = facturas_con_pago_amount + (item.amount_total-item.residual)
            facturas = record.invoice_paid_count = sum(self.env["account.invoice"].search(
                [("id", "in",record.invoice_ids.ids),("state", "not in",['cancel'])]
            ).mapped('amount_total'))
            record.invoice_balance = (facturas -facturas_con_pago_amount) - facturas_pagadas
    
    invoice_paid_count = fields.Char(compute="_compute_invoice_paid_count", string="")
    sin_iva = fields.Float(string="Valor del Crédito", required=False)
    con_iva = fields.Float(compute='_compute_con_iva', string='Valor de Crédito con IVA')
    product_id = fields.Many2one('product.product', string='Producto')
    impuestos = fields.Many2many('account.tax', string='Impuestos')
    diario = fields.Many2one('account.journal', string='Diario', default=lambda self: self.env['account.journal'].browse(2).id)
    account_id_product = fields.Many2one('account.account', string='Cuenta del Producto')
    account_id = fields.Many2one('account.account', string='Cuenta del Proveedor')
    cantidad_meses = fields.Integer(compute='_compute_cantidad_meses', string='Meses del Periodo')
    referencia = fields.Text(string="Referencia", required=False)
    
    @api.one
    @api.depends('fecha_inicio','fecha_vencimiento')
    def _compute_cantidad_meses(self):
        if self:            
            fecha_inicio = fields.Datetime.from_string(self.fecha_inicio) 
            fecha_vencimiento = fields.Datetime.from_string(self.fecha_vencimiento) 
            if fecha_inicio and fecha_vencimiento:
                self.cantidad_meses = self.diff_month(fecha_vencimiento,fecha_inicio)
    
    @api.onchange('product_id')
    def _compute_product_account(self):     
        if self.product_id:
            self.account_id_product = self.product_id.property_account_expense_id.id or False
            self.impuestos = self.product_id.supplier_taxes_id.ids

            if not self.account_id_product:
                return {'warning': {
            'title': 'Alerta!!!!',
            'message': 'Porfavor establezca una cuenta de gasto en el producto.'
        }}
            if not self.impuestos:
                return {'warning': {
            'title': 'Alerta!!',
            'message': 'Asegurese qué el el porcentaje de impuestos está establecido!!!'
        }}        

    @api.onchange('institucion')
    def _compute_account(self):     
        if self.institucion:
            self.account_id = self.institucion.property_account_payable_id.id or False
            if not self.account_id:
                return {'warning': {
            'title': 'Alerta!!!!',
            'message': 'Porfavor establezca una cuenta de pago en el proveedor.'
        }} 
    @api.one
    @api.depends('sin_iva','impuestos')
    def _compute_con_iva(self):        
        self.con_iva=self.sin_iva+self.sin_iva*(self.impuestos.amount/100) or 0
    
    
    def _compute_invoice_count(self):
        self.invoice_count = self.env["account.invoice"].search_count(
            [("id", "=", self.invoice_ids.ids)]
        )
        print(self.invoice_count)

    def _compute_invoice_paid_count(self):
        self.invoice_paid_count = self.env["account.invoice"].search_count(
            [("id", "=", self.invoice_ids.ids),("state", "in",['paid'])]
        )


    @api.one
    def crear_factura(vehicular_o_maquinaria):
        sequ = ''
        if vehicular_o_maquinaria._name in ['arrendamiento.vehicular']:
            sequ=vehicular_o_maquinaria.vehiculo_secuencia
        elif vehicular_o_maquinaria._name in ['arrendamiento.maquinaria']:
            sequ=vehicular_o_maquinaria.maquinaria_secuencia
        cantidad_meses = vehicular_o_maquinaria.cantidad_meses
        monto = vehicular_o_maquinaria.sin_iva / cantidad_meses
        ids_created = []
        for i in range(cantidad_meses):
            
            #print(fields.Datetime.from_string(vehicular_o_maquinaria.fecha_vencimiento)+relativedelta(months=+i))
            invoice = vehicular_o_maquinaria.env["account.invoice"]
            vals = {
            "origin": sequ,
            "type":"in_invoice",
            "state_files": "pending",
            "tipo_comprobante": "E",
            "journal_id": vehicular_o_maquinaria.diario.id,
            "user_id": 1,
            "company_id": 1,
            "partner_id": vehicular_o_maquinaria.institucion.id,
            "reference": vehicular_o_maquinaria.referencia,
            "date_invoice": fields.Datetime.from_string(vehicular_o_maquinaria.fecha_inicio)+relativedelta(months=+i),
            "date_due": fields.Datetime.from_string(vehicular_o_maquinaria.fecha_inicio)+relativedelta(months=+i),
            "invoice_line_ids": [
                [
                    0,
                    "virtual_107",
                    {
                        "sequence": 10,
                        "account_id": vehicular_o_maquinaria.account_id_product.id,
                        "quantity": 1,
                        "discount": 0,
                        "product_id": vehicular_o_maquinaria.product_id.id,
                        "name": sequ,
                        "purchase_line_id": False,
                        "purchase_id": False,
                        "asset_category_id": False,
                        "account_analytic_id": False,
                        "analytic_tag_ids": [[6, False, []]],
                        "uom_id": False,
                        "price_unit": monto,
                        "invoice_line_tax_ids":  [[6, False, vehicular_o_maquinaria.impuestos.ids]],
                    },
                ]
            ],
            "uso_cfdi": "G01",
            'account_id': vehicular_o_maquinaria.account_id.id
            }
            invoice_created = invoice.create(vals)
            ids_created.append(invoice_created.id)
        vehicular_o_maquinaria.invoice_ids = [(6,0,ids_created)]

    def get_invoices(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Facturas",
            "view_mode": "tree,form",
            "res_model": "account.invoice",
            "domain": [("id", "=", self.invoice_ids.ids)],
        }

    def get_invoices_paid(self):
        invoice_paid_ids = self.env["account.invoice"].search(
                    [("id", "=", self.invoice_ids.ids),("state", "in",['open']),("state", "in",['open'])]
                )
        invoice_ids = []
        for item in invoice_paid_ids:
            if item.residual != item.amount_total:
                invoice_ids.append(item.id)
        return {
            "type": "ir.actions.act_window",
            "name": "Facturas con Pago",
            "view_mode": "tree,form",
            "res_model": "account.invoice",
            "domain": [("id", "=", invoice_ids or [])],
        }

    def diff_month(self,d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
    

    @api.onchange('dia_de_pago')
    def onchange_dia_de_pago(self):
        if self.fecha_inicio and self.fecha_vencimiento:
            fecha_inicio = fields.Datetime.from_string(self.fecha_inicio)
            fecha_vencimiento = fields.Datetime.from_string(self.fecha_vencimiento) 
            fecha_inicio = fields.Date.from_string("%s-%s-%s"%(fecha_inicio.year,fecha_inicio.month,self.dia_de_pago))
            fecha_vencimiento = fields.Date.from_string("%s-%s-%s"%(fecha_vencimiento.year,fecha_vencimiento.month,self.dia_de_pago))
            self.fecha_inicio = fecha_inicio
            self.fecha_vencimiento = fecha_vencimiento
            print(self.fecha_vencimiento)

    @api.multi
    def facturas_arrendamiento(self):
        facturas_maquinaria = self.env['arrendamiento.maquinaria'].search([]).mapped('invoice_ids').ids
        facturas_arrendamiento = self.env['arrendamiento.vehicular'].search([]).mapped('invoice_ids').ids    
        print(facturas_maquinaria+facturas_arrendamiento)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'name': 'Facturas de Arrendamiento',
            'res_model': 'account.invoice',
            'target': 'current',
            'domain': [('id', 'in', facturas_maquinaria+facturas_arrendamiento)],
        }

        

      
