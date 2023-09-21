from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, timedelta,date


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def validate_cdp(self, partner_ids):
        payments = self.env['account.payment'].search(
            [('partner_id', 'in', partner_ids)])
        for payment in payments:
            payment_date = datetime.strptime(
                payment.payment_date, DEFAULT_SERVER_DATE_FORMAT).date()
            for invoice in payment.invoice_ids:
                if invoice.date_invoice:
                    invoice_date = datetime.strptime(
                        invoice.date_invoice, DEFAULT_SERVER_DATE_FORMAT)
                        
                    if not (payment_date.month == invoice_date.month and payment_date.year == invoice_date.year):                        
                        if payment.state_files == 'pending':
                            date_now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
                            current_date = datetime.strptime(date_now, DEFAULT_SERVER_DATE_FORMAT).date()
                            print(type(current_date-payment_date).days)
                            if (current_date-payment_date).days <=5:
                                pass
                            else:
                                raise UserError(
                                ('Cuenta con complementos de pago pendientes de cargar en el sistema.\n'+'Pago ID: '+str(payment.id)+'\nFecha de Pago:\t'+str(payment.payment_date)+'\nFecha Actual:\t'+str(date_now)+'\nDias transcurridos: '+str((current_date-payment_date).days)+str('\t')))


                            
