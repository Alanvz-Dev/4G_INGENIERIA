from odoo import _, api, fields, models
import datetime
from odoo.exceptions import ValidationError

class MisPedidosDeCompra(models.Model):
    _inherit = 'purchase.order'
    fecha_embarque=fields.Datetime(string='Fecha de Embarque:')
    pedido_recibido = fields.Selection(string='Estado del Pedido', selection=[('draft', 'No Confirmado'), ('done', 'Confirmado')],default='draft')
    fecha_de_recepcion_de_pedido = fields.Datetime(string='Confirmado el:')
    def valid(self):
        self.pedido_recibido='done'
        self.fecha_de_recepcion_de_pedido=datetime.datetime.now()
    
    @api.multi
    def write(self, values):
        #Solo para proveedor
        #Cuando pase a aprobado
        if not self.env['res.users'].has_group('purchase.group_purchase_user'):
            if self.fecha_embarque and self.pedido_recibido=='done':
                raise ValidationError("No puede cambiar la fecha y hora de embarque, por favor comuniquese con el departamento de compras.")
        return super(MisPedidosDeCompra, self).write(values)


    

    

