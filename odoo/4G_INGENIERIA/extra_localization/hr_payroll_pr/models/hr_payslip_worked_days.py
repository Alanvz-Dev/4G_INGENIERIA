from odoo import _, api, fields, models


class WorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.multi
    def name_get(self):
        res = []
        for rec in self:                                 
                res.append((rec.id, _("%s : %.2f Hora(s): %.2f") % (rec.name,rec.number_of_days, rec.number_of_hours)))
        return res
