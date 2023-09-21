from odoo import models, fields, api, _
from datetime import date, datetime, time, timedelta


class stock_picking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    ev1 = fields.Selection([('1', 'SI CUMPLE'), ('0', 'NO CUMPLE')], 'Documentacion Completa:',
                           help="Datos correctos: RFC, razon social, domicilio, CP, estipule OC en factura, estipular parcialidades.")
    ev2 = fields.Selection([('1', 'SI CUMPLE'), ('0', 'NO CUMPLE')], 'Especificaciones Acordadas:',
                           help="Revision de materiales contra documentos: coinciden cantidades, asi como, coincidencia de costos con lo cotizado.")
    ev3 = fields.Selection([('1', 'SI CUMPLE'), ('0', 'NO CUMPLE')], 'Tiempos de Entrega:',
                           help="Tiempos de arribo de material concuerde con la acordada con el comprador; en caso de no cumplir con el requerimiento que se solicita, hacer mencion del contratiempo para que se realice la anotacion en la OC.")
    ev4 = fields.Selection([('1', 'SI CUMPLE'), ('0', 'NO CUMPLE')], 'Cantidades Acordadas:',
                           help="Las cantidades acordadas deben cuadrar con lo arribado o facturado, en caso de generar parcialidad, se debe tener respaldo documentado de dicha parcialidad.")
    evpromedio = fields.Char('Promedio de Evaluacion:')

    @api.onchange('ev1', 'ev2', 'ev3', 'ev4')
    def onchange_evaluacion_proveedores(self):
        if self.ev1 != "1" or self.ev2 != "1" or self.ev3 != "1" or self.ev4 != "1":
            cero = 0
            self.evpromedio = cero
        else:
            uno = 1
            self.evpromedio = uno

    @api.onchange('pack_operation_product_ids')
    def onchange_stock_picking_validate(self):
        var = 0
        for valores in self.pack_operation_product_ids:
            if valores.qty_done > valores.product_qty:
                return {'warning': {'title': "Advertencia", 'message': "No puedes recibir mas producto del planeado, revisar el producto: %s" % (valores.product_id.name)}}
