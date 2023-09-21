from odoo import models, fields, api, _
from datetime import date, datetime, time, timedelta


class ev_proveedores(models.Model):
    _name = 'ev.proveedores'
    proveedor_partner_id = fields.Many2one(
        'res.partner', 'Nombre de Proveedor', default=1, domain=[('supplier', '=', True)])
    ev_1 = fields.Char('Evaluacion POSITIVA: ', readonly=True)
    ev_2 = fields.Char('Evaluacion NEGATIVA: ')
    ev_total = fields.Char('TOTAL DE CUMPLIMIENTO: ', readonly=True)
    fecha_inicio = fields.Datetime('Fecha inicio', default=fields.Datetime.now,
                                   help="Fecha de Inicio de la consulta")
    fecha_fin = fields.Datetime('Fecha fin', default=fields.Datetime.now,
                                help="Fecha de fin de la consulta")

    @api.onchange('proveedor_partner_id', 'fecha_inicio', 'fecha_fin')
    def onchange_proveedor_partner_id(self):
        fecha_i = datetime.strptime(
            self.fecha_inicio, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        fecha_f = datetime.strptime(
            self.fecha_fin, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")

        self.env.cr.execute("select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s and partner_id=%s group by partner_id; ",
                            (f_i, f_f, self.proveedor_partner_id.id))
        ev_totales = self.env.cr.fetchall()
        self.env.cr.execute("select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s and partner_id=%s and evpromedio='1'group by partner_id; ",
                            (f_i, f_f, self.proveedor_partner_id.id))
        ev_positiva = self.env.cr.fetchall()
        self.env.cr.execute("select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s and partner_id=%s and evpromedio='0'group by partner_id; ",
                            (f_i, f_f, self.proveedor_partner_id.id))
        ev_negativa = self.env.cr.fetchall()
        for proveedorestotales in ev_totales:
            self.ev_total = proveedorestotales[1]
            for proveedorespositiva in ev_positiva:
                self.ev_1 = (proveedorespositiva[1]*100)/proveedorestotales[1]
                for proveedoresnegativa in ev_negativa:
                    self.ev_2 = (
                        proveedoresnegativa[1]*100)/proveedorestotales[1]

    @api.multi
    def calcula_ev_proveedores(self):
        fecha_i = datetime.strptime(
            self.fecha_inicio, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        fecha_f = datetime.strptime(
            self.fecha_fin, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")

        self.env.cr.execute(
            " select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s group by partner_id; ", (f_i, f_f))
        ev_totales = self.env.cr.fetchall()
        self.env.cr.execute(
            " select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s and evpromedio='1'group by partner_id; ", (f_i, f_f))
        ev_positiva = self.env.cr.fetchall()
        totales = []
        for proveedorestotales in ev_totales:
            for proveedorespositiva in ev_positiva:
                if proveedorestotales[0] == proveedorespositiva[0]:
                    totales.append(proveedorestotales[1])
        return totales

    @api.multi
    def calcula_ev_proveedores_positiva(self):
        fecha_i = datetime.strptime(
            self.fecha_inicio, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        fecha_f = datetime.strptime(
            self.fecha_fin, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")

        self.env.cr.execute(
            "select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s group by partner_id; ", (f_i, f_f))
        ev_totales = self.env.cr.fetchall()
        self.env.cr.execute(
            "select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s and evpromedio='1'group by partner_id; ", (f_i, f_f))
        ev_positiva = self.env.cr.fetchall()
        positivas = []
        for proveedorestotales in ev_totales:
            for proveedorespositiva in ev_positiva:
                if proveedorestotales[0] == proveedorespositiva[0]:
                    positivas.append(
                        (proveedorespositiva[1]*100)/proveedorestotales[1])
        return positivas

    @api.multi
    def calcula_ev_proveedores_total_positiva(self):
        fecha_i = datetime.strptime(
            self.fecha_inicio, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        fecha_f = datetime.strptime(
            self.fecha_fin, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")

        self.env.cr.execute(
            "select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s group by partner_id; ", (f_i, f_f))
        ev_totales = self.env.cr.fetchall()
        self.env.cr.execute(
            "select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s and evpromedio='1'group by partner_id; ", (f_i, f_f))
        ev_positiva = self.env.cr.fetchall()
        total_positivas = []
        for proveedorestotales in ev_totales:
            for proveedorespositiva in ev_positiva:
                if proveedorestotales[0] == proveedorespositiva[0]:
                    total_positivas.append(proveedorespositiva[1])
        return total_positivas

    @api.multi
    def calcula_ev_proveedores_name(self):
        fecha_i = datetime.strptime(
            self.fecha_inicio, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        fecha_f = datetime.strptime(
            self.fecha_fin, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5)
        f_i = fecha_i.strftime("%Y-%m-%d %H:%M:%S")
        f_f = fecha_f.strftime("%Y-%m-%d %H:%M:%S")

        res_partner_obj = self.env['res.partner']
        self.env.cr.execute(
            "select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s group by partner_id; ", (f_i, f_f))
        ev_totales = self.env.cr.fetchall()
        self.env.cr.execute(
            "select partner_id, count(evpromedio) from stock_picking where scheduled_date between %s and %s and evpromedio='1'group by partner_id; ", (f_i, f_f))
        ev_positiva = self.env.cr.fetchall()
        proveedor_name = []
        for proveedorestotales in ev_totales:
            for proveedorespositiva in ev_positiva:
                if proveedorestotales[0] == proveedorespositiva[0]:
                    proveedor_name.append(res_partner_obj.search(
                        [('id', '=', proveedorestotales[0])]))
        return proveedor_name

    @api.multi
    def print_report_prov(self):

        return self.env['report'].get_action(self, 'purchaseorder_costos.template_evaluacion_proveedores')

    @api.multi
    def limpiar_consulta(self):

        self.ev_total = 0
        self.ev_1 = 0

        return
