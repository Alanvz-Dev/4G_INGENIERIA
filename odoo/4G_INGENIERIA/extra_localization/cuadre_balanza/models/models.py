# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
import pandas as pd
import io
import calendar
from odoo.exceptions import ValidationError


class cuadre_balanza(models.Model):
    _name = 'cuadre_balanza.cuadre_balanza'
    _rec_name='id'

    lines = fields.One2many('cuadre_balanza.line','id_cuadre_balanza', string='',ondelete='cascade')

    ano = fields.Selection([
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
    ], string='Año',required=True)

    cuadra = fields.Boolean()

    monto_debito = fields.Float(digits=(2,2),readonly=True)
    monto_credito = fields.Float(digits=(2,2),readonly=True)
    

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
    ], string='Mes',required=True)

    diferencia = fields.Integer(string='Diferencia', digits=(2, 2))

    def button_cuadre_balanza(self):
        print(len(self.lines))
        if not len(self.lines) >0:
            monto_debito=0
            monto_credito=0
            date_from = self.ano+'-'+self.mes+'-01'
            print(date_from)
            date_to = self.ano+'-'+self.mes+'-'+str(calendar.monthrange(int(self.ano),int(self.mes))[1])
            print(date_to)
            query = "select n1.id_movimiento poliza_debito,n1.sum monto_debito,n2.id_movimiento poliza_credito,n2.sum monto_credito from (select * from (select tabla_debito.id_movimiento,sum(debito) from ( select aml.id as id_apunte,aml.create_date,aml.write_date ,aa.code as codigo,aa.name as nombre ,aa.deprecated as descatalogado, aml.debit as debito ,aml.credit as credito, aml.contabilidad_electronica as check_apunte, am.contabilidad_electronica  as check_asiento, am.id as id_movimiento,aml.date as fecha_apunte, am.date as fecha_asiento from account_move_line aml inner join account_account aa on aml.account_id = aa.id inner join account_move am on am.id = aml.move_id where aml.move_id in (select id from account_move where contabilidad_electronica=true)  and aml.date between '"+date_from+"' and '"+date_to+"' order by aml.id,write_date,aml.debit ) as tabla_debito group by id_movimiento)  n1 ) n1 FULL JOIN (select * from (select tabla_credito.id_movimiento,sum(credito) from ( select aml.id as id_apunte,aml.create_date,aml.write_date ,aa.code as codigo,aa.name as nombre ,aa.deprecated as descatalogado, aml.debit as debito ,aml.credit as credito, aml.contabilidad_electronica as check_apunte, am.contabilidad_electronica  as check_asiento, am.id as id_movimiento,aml.date as fecha_apunte, am.date as fecha_asiento from account_move_line aml inner join account_account aa on aml.account_id = aa.id inner join account_move am on am.id = aml.move_id where aml.move_id in (select id from account_move where contabilidad_electronica=true)  and aml.date between '"+date_from+"' and '"+date_to+"' order by aml.id,write_date,aml.debit ) as tabla_credito group by id_movimiento) n2) n2 on (n1.id_movimiento=n2.id_movimiento)"
            print(query)
            self.env.cr.execute(query)
            vals=self.env.cr.dictfetchall()
            print(vals)
            poliza=0
            ids=[]
            for item in vals:
                if "{0:.2f}".format(item.get('monto_debito'))=="{0:.2f}".format(item.get('monto_credito')) and item.get('poliza_debito') and item.get('poliza_credito'):
                    item.update({'cuadra':True})
                    item.update({'diferencia':0})
                    monto_credito=monto_credito+float("{0:.2f}".format(item.get('monto_credito')))
                    monto_debito=monto_debito+float("{0:.2f}".format(item.get('monto_debito')))
                else:
                    print("{0:.2f}".format(item.get('monto_debito')),'\t',"{0:.2f}".format(item.get('monto_credito')))
                    item.update({'cuadra':False})
                    monto_credito=monto_credito+float("{0:.2f}".format(item.get('monto_credito')))
                    monto_debito=monto_debito+float("{0:.2f}".format(item.get('monto_debito')))
                    item.update({'diferencia':float("{0:.2f}".format(item.get('monto_debito')-item.get('monto_credito')))})
                line=self.env['cuadre_balanza.line'].create(item)
                ids.append(line.id)
                poliza=poliza+1

            self.lines=[(6,0, ids)]
            self.monto_debito=monto_debito
            self.monto_credito=monto_credito
            if monto_debito==monto_credito:
                self.cuadra=True
                self.diferencia=0.0
            else:
                self.cuadra=False
                self.diferencia=monto_debito-monto_credito
        
        elif len(self.lines) >0:
            raise ValidationError("Elimine el registro e inicie de nuevo...")


    def copy(self):
        vals={'ano':self.ano,'mes':self.mes}
        return self.create(vals)


            





        

class cuadre_balanza(models.Model):
    _name = 'cuadre_balanza.line'
    id_cuadre_balanza = fields.Many2one('cuadre_balanza.cuadre_balanza')
    
    #Debito
    monto_debito = fields.Integer(string='Monto Débito', digits=(2, 2))
    poliza_debito = fields.Many2one('account.move', string='Asiento Contable(Débito)')
    #Credito
    monto_credito = fields.Integer(string='Monto Crédito', digits=(2, 2))
    poliza_credito = fields.Many2one('account.move', string='Asiento Contable(Crédito)')

    cuadra = fields.Boolean(string='Cuadra')

    diferencia = fields.Integer(string='Diferencia', digits=(2, 2))


