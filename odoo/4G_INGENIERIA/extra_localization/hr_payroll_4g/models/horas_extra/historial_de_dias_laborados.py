from odoo import models, fields, api

class historial_de_dias_laborados(models.Model):
    _name = 'hr_payroll_4g.historial_de_tiempo'
    departamento = fields.Many2one('hr.department')
    operador = fields.Many2one('hr.employee')
    horas_de_trabajo_nomina_line = fields.Many2one('hr_payroll_4g.horas_de_trabajo_nomina')
    active = fields.Boolean(default=True)
    #Mostrar un check para definir si va a ser hora a fovor u hora en contra
    horas_a_favor = fields.Float()
    horas_en_contra = fields.Float()
    state = fields.Selection([('to_approve', 'Pendiente de Aprobar'),('approve', 'Aprobado'),('refuse', 'Rechazado'),('paid', 'Pagado'), ('to_paid', 'Para Pago')], string='Estado', default='to_approve')
    #cambiar extra por nómina
    tipo_pago = fields.Selection([('undef', 'Indefinido'),('extra', 'Tiempo extra(Pagar en Nómina)'),('txt', 'Tiempo Por Tiempo')], string='Estado', default='undef')

    #Si es tiempo extra buscar la nómina perteneciente
    fecha_pago = fields.Date()