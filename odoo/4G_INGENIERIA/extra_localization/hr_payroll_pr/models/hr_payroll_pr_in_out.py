from numpy import diff
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime,timedelta
import pytz

class InOut(models.Model):
    _name = 'hr_payroll_pr.in_out'
    _description = '(Inc4G) Entrada y Salida Guardia'
    date_in = fields.Datetime(string='Entrada')
    date_out = fields.Datetime(string='Salida')
    total = fields.Float(compute='_compute_total',store=True)
    total_checador = fields.Float(compute='_compute_total',store=True)
    bono_puntualidad = fields.Boolean(compute='_compute_total',store=True)
    mayordomia_line_id = fields.Many2one('hr_payroll_pr.mayordomia_line')


    @api.depends('date_in', 'date_out')
    def _compute_total(self):
        for item in self:
            try:
                #aml = ac_move.line_ids.filtered(lambda x:aml = ac_move.line_ids.filtered(lambda x: x.account_id.reconcile or x.account_id.internal_type == 'liquidity') x.account_id.reconcile or x.account_id.internal_type == 'liquidity')

                if (item.date_in) and (item.date_out):
                    numero_de_dia=item.mayordomia_line_id.operador.turno.dia_de_la_semana(item.mayordomia_line_id.mayordomia_id.fecha)
                    turno_line=item.mayordomia_line_id.operador.turno.turno_line_ids.filtered(lambda x: x.turno_id.id ==item.mayordomia_line_id.operador.turno.id and x.dia==numero_de_dia[0])
                    print(turno_line)
                    #turno_line=item.mayordomia_line_id.operador.turno.turno_line_ids.search([('turno_id','in',[item.mayordomia_line_id.operador.turno.id]),('dia','in',numero_de_dia)])
                    delta=timedelta(days=0)
                    if turno_line.between_days:
                        delta = timedelta(days=1)
                    entrada_empresa = item.mayordomia_line_id.mayordomia_id.fecha+item.mayordomia_line_id.mayordomia_id.float_to_time_str(turno_line.hour_from)
                    salida_empresa = item.mayordomia_line_id.mayordomia_id.fecha+item.mayordomia_line_id.mayordomia_id.float_to_time_str(turno_line.hour_to)
                    entrada_empresa_dt =datetime.strptime(entrada_empresa, DEFAULT_SERVER_DATETIME_FORMAT)
                    salida_empresa_dt =datetime.strptime(salida_empresa, DEFAULT_SERVER_DATETIME_FORMAT)+delta   
                    entrada_empresa = datetime.strftime(entrada_empresa_dt,DEFAULT_SERVER_DATETIME_FORMAT)
                    salida_empresa = datetime.strftime(salida_empresa_dt,DEFAULT_SERVER_DATETIME_FORMAT) 
                    print(salida_empresa)
                    # salida_empresa =
                    date_in_company = self.utc_to_local(datetime.strftime(self.local_to_utc(entrada_empresa),DEFAULT_SERVER_DATETIME_FORMAT))
                    date_out_company = self.utc_to_local(datetime.strftime(self.local_to_utc(salida_empresa),DEFAULT_SERVER_DATETIME_FORMAT))
                    date_out = self.utc_to_local(item.date_out)
                    date_in = self.utc_to_local(item.date_in)
                    #Si entro mas temprano considera la hora de entrada de de la empresa o si llego con +5 minutos de tolarancia
                    if date_in<=date_in_company+timedelta(minutes=5):
                        date_in = date_in_company
                        item.bono_puntualidad=True
                    if (date_out>date_out_company):
                        date_out = date_out_company
                    if (date_out<date_out_company):
                        item.bono_puntualidad=False                                                                    
                    diference = date_out-date_in
                    item.total = (diference.total_seconds())/3600
                    if item.total<0:
                        item.total=0
                    item.total_checador=((datetime.strptime(item.date_out,DEFAULT_SERVER_DATETIME_FORMAT)-datetime.strptime(item.date_in,DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds())/3600

                else:
                    item.total = 0
                    item.bono_puntualidad=False
            except:
                pass

    @api.multi
    def name_get(self):
        res = []
        for rec in self:                                 
                res.append((rec.id, _("%s - %s (%.2f Horas) (%.2f Horas Checador)") % (self.utc_to_local_to_str(rec.date_in)[11:16],self.utc_to_local_to_str(rec.date_out)[11:16], rec.total,rec.total_checador)))
        return res

    def utc_to_local(self,date):
        local = pytz.timezone("America/Mexico_City")
        return pytz.utc.localize(datetime.strptime(date,DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)#,DEFAULT_SERVER_DATETIME_FORMAT

    def utc_to_local_to_str(self,date):
        local = pytz.timezone("America/Mexico_City")
        return datetime.strftime(pytz.utc.localize(datetime.strptime(date,DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),DEFAULT_SERVER_DATETIME_FORMAT)
       
    def local_to_utc(self,date):
        #Las 7:00 am de Ciudad de Mexico son las 13:00:00 en UTC
        local = pytz.timezone("America/Mexico_City")
        naive = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt

    @api.onchange('date_in','date_out')
    def _onchange_dates(self):
        self._compute_total()
    
    def unlink_performance(self,ids):
        # Delete followers for models that will be unlinked.
        # x = tuple(ids)
        # x = str(x)
        query = ("DELETE FROM hr_payroll_pr_in_out WHERE id IN %s" % str(tuple(ids)))
        self.env.cr.execute(query)
        



    
    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        print(values)
        result = super(InOut, self).create(values)
    
        return result
    

    

