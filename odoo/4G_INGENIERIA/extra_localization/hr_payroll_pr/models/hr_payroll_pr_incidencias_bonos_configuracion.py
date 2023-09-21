from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ModuleName(models.Model):
    _name = 'hr_payroll_pr.incidencias_bonos_configuracion'
    _description = 'Configuracion de Bonos Para Descuento'
    _rec_name='name'
    incidencia_id = fields.Many2one('hr_payroll_pr.incidencias', string='Incidencia')
    asistencia = fields.Boolean(string='Bono Asistencia')
    puntualidad = fields.Boolean(string='Bono Puntualidad')
    informativo = fields.Boolean(string='Solo Informativo')
    name = fields.Char(compute='_compute_name', string='Nombre')
    diferencia_de_horas = fields.Boolean(string='Diferencia de Horas')
    dias_trabajados = fields.Boolean(string='Considerar en Nómina')

    @api.multi
    def _compute_name(self):
        for record in self:
            if not record.informativo:
                record.name = '%s %s %s' % (record.incidencia_id.codigo,("Desc. Bono de Asistencia", "No Desc. Bono de Asistencia")[record.asistencia],("Desc. Bono de Puntualidad", "No Desc. Bono de Puntualidad")[record.puntualidad])
            else:
                record.name = 'Solo Informativo'
            
    
    @api.constrains('informativo')
    def _check_informativo(self):
        for record in self:
            if record.informativo and (record.asistencia or record.puntualidad):
                raise UserError('Asistencia Y/O Puntualidad no pueden estar establecidos cuando se establece el valor Informativo')
