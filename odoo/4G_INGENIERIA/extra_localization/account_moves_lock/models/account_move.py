from odoo import api, models, _
from odoo.exceptions import UserError
import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def _check_lock_date(self):
        res = super()._check_lock_date()
        periods_to_lock=self.env['account_moves_lock.account_moves_lock'].search([])
        is_valid=False
        for move in self:
            if not periods_to_lock:
                is_valid=False
            else:
                for period in periods_to_lock:
                    TODAY_CHECK = datetime.datetime.strptime(move.date, DEFAULT_SERVER_DATE_FORMAT)
                    start = datetime.datetime.strptime(period.start_date, DEFAULT_SERVER_DATE_FORMAT)
                    end = datetime.datetime.strptime(period.end_date,DEFAULT_SERVER_DATE_FORMAT)
                    message=''
                    if TODAY_CHECK>= start   and TODAY_CHECK<= end:
                        is_valid=True
                        nb_draft_entries = self.env['account.move'].search([('state', 'in', ['draft']),('contabilidad_electronica', 'in', [True])])
                        if nb_draft_entries:
                            move_names=''
                            for item in nb_draft_entries:
                                move_names=move_names+' '+item.name+' '
                            message = _("No se pudo generar el Movimiento.\n"+"Los asientos contables:\n"+" "+move_names+'\t'+str(item.ids)+"\nSe encuentran sin validar.\nPor favor valídelos o eliminelos e intente nuevamente")
                            raise UserError(message)
                        return res
        if not self:
            return True                            
        if not is_valid:
            message = _("No se pudo generar el Movimiento.\n No existe ningún periodo Abierto que corresponda a la fecha \t"+move.date)
            raise UserError(message)
