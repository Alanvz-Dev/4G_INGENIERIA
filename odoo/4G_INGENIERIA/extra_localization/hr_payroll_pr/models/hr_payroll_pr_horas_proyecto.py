from odoo import _, api, fields, models


class EmpleadosAdministrativos(models.Model):
    _name = 'hr_payroll_pr.horas_proyecto'
    _rec_name = 'name'
    name = fields.Char(compute='_compute_name', string='Nombre')
    mayordomia_line_id = fields.Many2one('hr_payroll_pr.mayordomia_line', string='Mayordomía Line')
    empleado = fields.Many2one('hr.employee', string='Empleado',related='mayordomia_line_id.operador',store=True)
    monto = fields.Float(compute='_compute_monto', string='Monto',store=True)
    centro_de_trabajo = fields.Many2one(comodel_name='mrp.workcenter', string='Centro de Trabajo')

    @api.depends('horas')
    def _compute_monto(self):
        for record in  self:
            print(record.empleado)
            if record.empleado.contract_id.sueldo_integrado>0:
                record.monto = record.horas * (record.empleado.contract_id.sueldo_integrado)/8
        
    

    @api.depends('analytic_account_id','horas')
    def _compute_name(self):
        for rec in self:
            if rec.analytic_account_id and rec.horas:
                rec.name= '%s %.2f Hora(s)' %(rec.analytic_account_id.name[:12],rec.horas)
            else:
                rec.name="No válido, por favor revise que el registro contenga proyecto y horas."

    analytic_account_id = fields.Many2one('account.analytic.account',string='Proyecto')
    horas = fields.Float(string='Horas', digits=(2,1))



