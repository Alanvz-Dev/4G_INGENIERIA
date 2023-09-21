from odoo import _, api, fields, models
import uuid


class InBatch(models.TransientModel):
    _name = 'hr_4g_payroll_ext.incwiz'
    _inherit = 'hr_4g_payroll_ext.incidency'

    _description = '(Inc4G) Ingresar Incidencias Masivamente'
    employee_ids = fields.Many2many(comodel_name='hr.employee')
    agregar_nota = fields.Boolean()
    nota = fields.Text(string='Nota')
    
    def crear_incidencias(self):
        _uuid = uuid.uuid4().hex
        for employee in self.employee_ids:
            vals = {
                'active': True,
                'considerar_dias': self.considerar_dias,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'dias': self.dias,
                'employee_id': employee.id,
                'horas': self.horas,
                'tipo': self.tipo,
                'tipo_incidencia': self.tipo_incidencia,
                'calendario': self.calendario.id,
                'employee_ids':False,
                
            }
            if self.agregar_nota:
                vals.update({'uuid':_uuid})
                created = self.env[self._inherit].create(vals)
                created.message_post(body=self.nota,
                          subtype="mail.mt_comment",
                          type="comment")
            else:
                created = self.env[self._inherit].create(vals)
            
            
