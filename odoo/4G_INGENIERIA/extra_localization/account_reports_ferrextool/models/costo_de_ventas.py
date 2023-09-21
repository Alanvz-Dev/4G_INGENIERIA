from odoo import _, api, fields, models
import pandas as pd
import io
import calendar
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
from datetime import datetime


class CostoDeVentas(models.Model):
    _name = 'costo_de_ventas.vista'
    _rec_name='rec_name'
    cdv_lines = fields.One2many(
        'costo_de_ventas.line', 'cdv_vista_id', string='')
    mes = fields.Selection([
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ], string='Mes', required=True)

    ano = fields.Selection([
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
    ], string='Año', required=True)

    total = fields.Float(compute='_compute_total', string='Total')

    rec_name = fields.Char(compute='_compute_fields_combination')

    def _compute_fields_combination(self):
        self.rec_name='COSTO DE VENTAS'+'/'+self.mes+'/'+self.ano

    @api.one
    def _compute_total(self):
        costo_de_produccion=0
        inventarios=0
        importe=0
        if self.cdv_lines:
            for line in self.cdv_lines:
                if line.tipo=='inventario':
                    costo_de_produccion=costo_de_produccion+line.importe
                elif line.tipo=='compras':
                    costo_de_produccion=costo_de_produccion+line.importe
                elif line.tipo=='fletes':
                    costo_de_produccion=costo_de_produccion+line.importe
                elif line.tipo=='inventario_f':
                    importe=importe+abs(line.importe)
                print(line)
            self.total=costo_de_produccion-importe
            print(self.total)
        else:
            self.total=0.0
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Validado')
    ], string='Estatus', default='draft')
    move_id = fields.Many2one('account.move')

    def validar(self):
        if self.move_id:
            if self.move_id.state=='posted' or self.move_id.contabilidad_electronica==True:
                raise ValidationError("Existe un Apunte Validado. \nDebe cancelar el Apunte contable para establecer para recalcular el nuevo.")
            else:
                self.move_id.unlink()
        if self.total>0:
            move = self.env['account.move'].create(
                {
                    "date": datetime.today(),
                    "journal_id": 3,
                    "ref": "COSTO DE VENTAS",
                    "contabilidad_electronica": False,
                    "line_ids": [
                        [
                            0,
                            "virtual_722",
                            {
                                "account_id": 2832,
                                "amount_currency": 0,
                                "currency_id": False,
                                "debit": self.total,
                                "credit": 0,
                                "partner_id": False,
                                "name": False,
                                "analytic_account_id": False,
                                "analytic_tag_ids": [[6, False, []]],
                                "date_maturity": False,
                                "contabilidad_electronica": True,
                            },
                        ],
                        [
                            0,
                            "virtual_740",
                            {
                                "account_id": 2905,
                                "amount_currency": 0,
                                "currency_id": False,
                                "debit": 0,
                                "credit": self.total,
                                "partner_id": False,
                                "name": False,
                                "analytic_account_id": False,
                                "analytic_tag_ids": [[6, False, []]],
                                "date_maturity": False,
                                "contabilidad_electronica": True,
                            },
                        ],
                    ],
                    "narration": False,
                }
            )
            move.post()
            self.move_id=move.id
            self.state = 'done'
        else:
            raise ValidationError("No puede Generar este Apunte contable en Cero.")

    @api.multi
    def unlink(self):
        # "your code"
        if self.move_id:
            if self.move_id.state=='posted' or self.move_id.contabilidad_electronica==True:
                raise ValidationError("Debe cancelar el Apunte contable para establecer a Borrador.")
            else:
                return super(CostoDeVentas, self).unlink()
        elif not self.move_id:
            return super(CostoDeVentas, self).unlink()
        

    def cancelar(self):
        self.state = 'cancel'

    def borrador(self):
        if self.move_id:
            if self.move_id.state=='posted' or self.move_id.contabilidad_electronica==True:
                raise ValidationError("Debe cancelar el Apunte contable para establecer a Borrador.")
            else:
                self.state = 'draft'
        

    def calcular_costo_de_ventas(self):
        if not self.cdv_lines:
            self.env['trial.balance.report.wizard.contabilidad.cfdi'].costo_de_ventas(
                self)
        else:
            raise ValidationError("Por favor cree un registro nuevo.")


class CostoDeVentasLine(models.Model):
    _name = 'costo_de_ventas.line'
    cdv_vista_id = fields.Many2one('costo_de_ventas.vista')
    concepto = fields.Char(string='CONCEPTO')
    importe = fields.Float(string='IMPORTE')
    tipo = fields.Selection(selection=[('fletes', 'Fletes'), ('compras', 'Compras'),('inventario', 'Inventario'),('inventario_f', 'Inventario Final')])
