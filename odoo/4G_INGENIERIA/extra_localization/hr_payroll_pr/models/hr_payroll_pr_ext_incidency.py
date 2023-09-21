from odoo import _, api, fields, models

class Incidencia(models.Model):
    _inherit = 'hr_4g_payroll_ext.incidency'
    color = fields.Integer(compute='_compute_color', string='Color')
    
    @api.depends('state')
    def _compute_color(self):
        for item in self:
            if item.state=='done':
                item.color=10
            elif item.state=='draft':
                item.color=9
            elif item.state=='pending':
                item.color=12
            elif item.state:
                item.color=8            

    @api.multi
    def name_get(self):
        res = []
        for incidency in self:   
            incidency.tipo_incidencia
            incidency.dias 
            incidency.horas
            incidency.state
            administrative_name=''
            if incidency.employee_id.is_administrativo:
                administrative_name='Administrativo'
            res.append((incidency.id, _("%s %.2f dia(s) %.2f hora(s) %s" % (incidency.tipo_incidencia,abs(incidency.dias),abs(incidency.horas),administrative_name))))
        return res

    @api.model
    def create(self, values):
        print(values)
        date =''
        if 'fecha_bono' in values:
            if values['fecha_bono']:
                date = values['fecha_bono']
        if 'date_from' in values:
            if values['date_from']:
                date = values['date_from'][:10]        
        self.env['hr_payroll_pr.mayordomia'].search([('fecha','in',[date])]).check_close()
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'hr_4g_payroll_ext.incidency') or _('New')
        result=super(Incidencia, self).create(values)

        return result