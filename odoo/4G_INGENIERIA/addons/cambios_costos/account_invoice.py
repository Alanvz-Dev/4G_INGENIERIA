# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from odoo.exceptions import UserError,RedirectWarning,ValidationError
from datetime import datetime, date, time, timedelta
import calendar

class account_invoice(models.Model):
    _name='account.invoice'
    _inherit='account.invoice'
    fecha_pago=fields.Date(string='Fecha de Pago')
    fecha_pagop=fields.Date(string='Fecha de Pago P')
    prueba=fields.Char(string='Dias-Vencido', reandonly=True)
    campo_referencia=fields.Char(string='Referencia')
    campo_referencia_computed=fields.Char(compute='_compute_under_minimum',string='ReferenciaXD')
    cdp=fields.Boolean('Complemento Pago')
    factoraje=fields.Boolean('Factoraje')
    refacturacion=fields.Boolean('Refacturacion')
    applybono=fields.Boolean('No aplica bono')



    @api.one	
    @api.constrains('date_due')
    def _cambio_prueba(self):
        fechapago=self.date_due
        formato_fecha="%Y-%m-%d"
        fecha = datetime.today()
        fecha_actual= fecha.strftime(formato_fecha)
        fecha1 = datetime.strptime(fechapago, formato_fecha)
        fecha2 = datetime.strptime(fecha_actual, formato_fecha)
        diferencia = fecha1 - fecha2
        var=diferencia.days
        var2= str(var)
        self.prueba=var2  
	
    @api.one
    def _compute_under_minimum(self):
        if not self.campo_referencia:
            self.write({"campo_referencia":str(self.name)}) 

    # @api.one    
    # @api.constrains('fecha_pagop')
    # def _onchange_fecha_pago(self):      
    #     reference=self.reference
    #     fecha_pagop=self.fecha_pagop
    #     partner_id=self.partner_id
    #     self.env.cr.execute("SELECT id FROM res_partner WHERE parent_id= %s" %(partner_id.id))
    #     parent_id2=self.env.cr.fetchall()
    #     for parentid in parent_id2:
    #         try:
    #             self.env.cr.execute(" SELECT id FROM cxp_proveedores WHERE invoice_select_name LIKE  '%%"+"Factura: /"+(reference)+"%%' AND partner_id=%s" % (parentid[0]))
    #             cxp_id=self.env.cr.fetchall()
    #             for cid in cxp_id:
    #                 self.env.cr.execute(" UPDATE cxp_proveedores SET fecha_pago='%s' WHERE id=%s" % (fecha_pagop,cid[0]))
    #                 self.env.cr.execute(" UPDATE cxp_proveedores SET state='parapago' WHERE id=%s" % (cid[0]))
    #         except:
    #             print('x')

class stock_move(models.Model):
    _name='stock.move'
    _inherit='stock.move'
    basura=fields.Boolean('bs')



						

		






