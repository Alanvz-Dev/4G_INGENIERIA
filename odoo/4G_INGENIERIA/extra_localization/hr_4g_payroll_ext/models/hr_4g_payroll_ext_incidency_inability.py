from odoo import _, api, fields, models


class Inability(models.Model):
    _name = 'hr_4g_payroll_ext.incidency_inability'
    _description = '(Inc4G) Incapacidades'
    ramo_seguro = fields.Selection([('Riesgo de trabajo', 'Riesgo de trabajo'), ('Enfermedad general', 'Enfermedad general'), ('Maternidad','Maternidad')], string='Ramo de seguro')
    tipo_de_riesgo = fields.Selection([('Accidente de trabajo', 'Accidente de trabajo'), ('Accidente de trayecto', 'Accidente de trayecto'), ('Enfermedad de trabajo','Enfermedad de trabajo')], string='Tipo de riesgo')
    secuela = fields.Selection([('Ninguna', 'Ninguna'), ('Incapacidad temporal', 'Incapacidad temporal'), ('Valuación inicial provisional','Valuación inicial provisional'), ('Valuación inicial definitiva', 'Valuación inicial definitiva')], string='Secuela')
    control = fields.Selection([('Unica', 'Unica'), ('Inicial', 'Inicial'), ('Subsecuente','Subsecuente'), ('Alta médica o ST-2', 'Alta médica o ST-2')], string='Control')
    control2 = fields.Selection([('01', 'Prenatal o ST-3'), ('02', 'Enalce'), ('03','Postnatal')], string='Control maternidad')
    folio_incapacidad = fields.Char('Folio de incapacidad')
    porcentaje = fields.Char('Porcentaje')
    incidency_id = fields.Many2one('hr_4g_payroll_ext.incidency')













