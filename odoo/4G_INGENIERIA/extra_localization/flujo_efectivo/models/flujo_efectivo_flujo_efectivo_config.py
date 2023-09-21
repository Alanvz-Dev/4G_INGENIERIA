# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime,timedelta
from odoo.tools.safe_eval import safe_eval
import calendar
from odoo.exceptions import  ValidationError



class flujo_efectivo_config(models.Model):
    _name = 'flujo_efectivo.flujo_efectivo_config'
    _rec_name = 'categoria'
    _order = 'sequence'
    sequence = fields.Integer(default=0,help="Gives the sequence order when displaying a list of records.")



    tipo = fields.Selection(
        string='Tipo de Flujo',
        selection=[('in', 'Ingreso'), ('out', 'Egreso')]
    )
    monto_de_prsupuesto = fields.Selection(
        string='Monto de Presupuesto',
        selection=[('f', 'Forecast'),('ip', 'Importe Planifiacado'), ('ir', 'Importe Real')]
    )  
    active = fields.Boolean(string='Activo',default=True)
    descripcion = fields.Char(string="Descripciòn")
    intervalo_de_dezplazamiento = fields.Integer(string='Intervalo de Dezplazamiento')
    entidad = fields.Char(string='Entidad') #sub_sub_tipo_id
    categoria = fields.Char(string='Categorìa')
    sub_categoria = fields.Char(string='Subcategorìa')
    code = fields.Text(string='Còdigo Python',default="""
                    # Variables disponibles:
                    #----------------------
                    # instance: objeto equivalente a self
                    # current_config: objecto actual (flujo_efectivo_config)
                    # calendar: libreria calenda
                    # datetime: libreria datetime
                    # timedelta: libreria timedelta
                    # DEFAULT_SERVER_DATE_FORMAT: formato para fechas del servidor
                    # DEFAULT_SERVER_DATETIME_FORMAT: formato para fechas hora del servidor
                    # flujo_de_efectivo: instancia del modelo flujo_efectivo.flujo_efectivo
                    # Nota: Se deben de crar los registros de la siguiente manera
                    
                    #                           vals = {
                    #                           'monto':factura.residual,
                    #                           'tipo':'out',
                    #                           'fecha_programada':record.start_date,
                    #                           'categoria':current_config.categoria,
                    #                           'entidad':factura.partner_id.name
                    #                           }
                    #                           flujo_de_efectivo.create(vals)
                    """)

    def fecha_dezplazada(date,days):
            delta = timedelta(days=days)
            datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)+delta 
            return datetime.strftime(datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)+delta ,DEFAULT_SERVER_DATETIME_FORMAT)                


    @api.multi
    def calcular(self):
        configs = self.search([])
        for config in configs:
            class BrowsableObject(object):
                def __init__(self, env):
                    self.env = env
            instance = BrowsableObject(self.env)
            flujo_de_efectivo = instance.env['flujo_efectivo.flujo_efectivo']
            current_config = config
            baselocaldict = {'instance': instance,'current_config':current_config,'calendar':calendar,'datetime':datetime,'timedelta':timedelta,
            'DEFAULT_SERVER_DATE_FORMAT':DEFAULT_SERVER_DATE_FORMAT,'DEFAULT_SERVER_DATETIME_FORMAT':DEFAULT_SERVER_DATETIME_FORMAT,'flujo_de_efectivo':flujo_de_efectivo}
            localdict = dict(baselocaldict)
            try:
                safe_eval(config.code, localdict, mode='exec', nocopy=True)
            except Exception as e:
                raise ValidationError("Error en la configuración %s %s     %s" % (config.id,config.categoria,e))
            

 



















































