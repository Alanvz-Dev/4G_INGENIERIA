# -*- coding: utf-8 -*-


from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import base64
from datetime import date, datetime, time, timedelta
import time
from dateutil.relativedelta import relativedelta


class report_ventas(models.Model):
    _name = "report.ventas"
    fecha_inicio = fields.Datetime("Fecha inicio:")
    fecha_fin = fields.Datetime("Fecha Fin:")
    cliente = fields.Many2one("res.partner", "Cliente")
    ruta_view = fields.Selection(
        [("1", "Ruta 1"), ("2", "Ruta 2"), ("3", "Ruta 3")], "Ruta")

    @api.multi
    def show_data_report_ventas(self):
        fecha_i = datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S")
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        fecha_f = datetime.strptime(self.fecha_fin, "%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")
        report_array = []
        self.env.cr.execute(" select rp.name,sum(ac.amount_untaxed) from account_invoice ac join res_partner rp on ac.partner_id=rp.id where ac.invoice_datetime between %s and %s and ac.state != 'cancel' and ac.state != 'draft' group by rp.name;", (f_i, f_f))
        report_details = self.env.cr.fetchall()
        for valores in report_details:
            report_array.append(valores)
        return report_array

    @api.multi
    def show_report_ventas_clientes(self):
        fecha_i = datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S")
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        fecha_f = datetime.strptime(self.fecha_fin, "%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")
        report_array = []
        self.env.cr.execute(" select rp.name,ac.invoice_datetime,ac.amount_untaxed from account_invoice ac join res_partner rp on ac.partner_id=rp.id where ac.state != 'cancel' and ac.state != 'draft' and rp.id=%s  and ac.invoice_datetime between %s and %s order by ac.invoice_datetime asc;", (self.cliente.id, f_i, f_f))
        report_details = self.env.cr.fetchall()
        for valores in report_details:
            report_array.append(valores)
        return report_array

    @api.multi
    def show_report_ventas_clientes_total(self):
        fecha_i = datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S")
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        fecha_f = datetime.strptime(self.fecha_fin, "%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")
        report_array = []
        self.env.cr.execute(" select sum(ac.amount_untaxed) from account_invoice ac join res_partner rp on ac.partner_id=rp.id where ac.state != 'cancel' and ac.state != 'draft' and rp.id=%s  and ac.invoice_datetime between %s and %s;", (self.cliente.id, f_i, f_f))
        report_details = self.env.cr.fetchall()
        for valores in report_details:
            report_array.append(valores)
        return report_array

    @api.multi
    def show_report_ventas_rutas(self):
        fecha_i = datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S")
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        fecha_f = datetime.strptime(self.fecha_fin, "%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")
        report_array = []
        self.env.cr.execute(" select rp.name,ac.invoice_datetime,ac.amount_untaxed from account_invoice ac join res_partner rp on ac.partner_id=rp.id where ac.state != 'cancel' and ac.state != 'draft' and rp.ruta=%s and ac.invoice_datetime between %s and %s order by ac.invoice_datetime asc;", (self.ruta_view, f_i, f_f))
        report_details = self.env.cr.fetchall()
        for valores in report_details:
            report_array.append(valores)
        return report_array

    @api.multi
    def show_report_ventas_rutas_total(self):
        fecha_i = datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S")
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        fecha_f = datetime.strptime(self.fecha_fin, "%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")
        report_array = []
        self.env.cr.execute("select sum(ac.amount_untaxed) from account_invoice ac join res_partner rp on ac.partner_id=rp.id where ac.state != 'cancel' and ac.state != 'draft' and rp.ruta=%s  and ac.invoice_datetime between %s and %s;", (self.ruta_view, f_i, f_f))
        report_details = self.env.cr.fetchall()
        for valores in report_details:
            report_array.append(valores)
        return report_array

    @api.multi
    def print_ventas(self):
        return self.env["report"].get_action(self, "report_ventas.template_report_ventas")

    @api.multi
    def print_ventas_clientes(self):
        return self.env["report"].get_action(self, "report_ventas.template_report_ventas_clientes")

    @api.multi
    def print_ventas_rutas(self):
        return self.env["report"].get_action(self, "report_ventas.template_report_ventas_rutas")


class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    ruta = fields.Selection(
        [("1", "Ruta 1"), ("2", "Ruta 2"), ("3", "Ruta 3")], "Ruta")