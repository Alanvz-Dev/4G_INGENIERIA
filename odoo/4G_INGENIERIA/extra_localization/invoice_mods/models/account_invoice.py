from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Invoice(models.Model):
    _inherit = 'account.invoice'

    gr = fields.Char(string='GR')
    gr_count = fields.Integer(compute='_compute_gr_count', string="Contador GR(Días)")
    evidencia_recibida = fields.Boolean()

# No entra a debug, se necesita poner un api.depends para que entre al debug cuando se hace un cambio
    @api.one
    def _compute_gr_count(self):
        if self.gr == "" or self.gr == False or self.gr == None:
            if self.date_invoice:
                days=(datetime.now()-datetime.strptime(self.date_invoice,DEFAULT_SERVER_DATE_FORMAT))
                self.gr_count=days.days
        else:
            pass

    

    


    
    
