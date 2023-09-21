from odoo import models, fields, api

class flujo_efectivo(models.Model):
    _name = 'flujo_efectivo.flujo_efectivo' 
    _rec_name = 'categoria'
    tipo = fields.Selection(
        string='Tipo de Flujo',
        selection=[('in', 'Ingreso'), ('out', 'Egreso')]
    )      
    categoria = fields.Char(string='Categorìa')
    sub_categoria = fields.Char(string='Subcategorìa')
    entidad = fields.Char(string='Entidad')
    fecha_programada = fields.Date()
    monto = fields.Float( digits=(12, 2))
    id_registro = fields.Integer(string='Id De Registro') 
    fecha_pago = fields.Date(string='Fecha de Pago(En caso de ser cŕedito)')
    def obtener_vistas(self):
        self.search([]).unlink()
        self.env['flujo_efectivo.flujo_efectivo_config'].calcular()

                
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reporte',
            'res_model': 'flujo_efectivo.flujo_efectivo',
            'view_mode': 'pivot,tree,form',
            'target': 'current'
        }

    @api.multi
    def write(self, values):
        # CODE HERE
        if 'monto' in values:
            balance_bank = self.env['flujo_efectivo.balance_bank'].browse(self.id_registro)
            balance_bank.monto = values['monto']
        return super(flujo_efectivo, self).write(values)
