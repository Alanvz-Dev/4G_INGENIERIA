from odoo import _, api, fields, models

class FlujoEfectivo(models.Model):
    _name = 'escenario_de_ventas.flujo_de_efectivo'
    _description = 'New Description'
    sale_id = fields.Many2one('sale.order')
    test_1 = fields.Float(string='Aceros Total', digits=(12, 2))
    test_2 = fields.Float(string='Aceros PZ', digits=(12, 2))

    test_3 = fields.Float(string='Perifericos Total', digits=(12, 2))
    test_4 = fields.Float(string='Perifericos PZ', digits=(12, 2))

    test_5 = fields.Float(string='Otros Prod', digits=(12, 2))
    test_6 = fields.Float(string='Otros ProdPZ', digits=(12, 2))

    test_7 = fields.Float(string='Otros Gastos/Fle/Maq Total', digits=(12, 2))
    test_8 = fields.Float(string='Otros Gastos/Fle/Maq PZ', digits=(12, 2))

    test_9 = fields.Float(string='Total PZ', digits=(12, 2))
    test_10 = fields.Float(string='Tota PZ PZ', digits=(12, 2))
    line_id = fields.Many2one(comodel_name='escenario_de_ventas.flujo_de_efectivo_line', string='Line') 
    
    def test(self):
        escenario_de_ventas = self.env['escenario_de_ventas.escenario_de_ventas'].search([])
        len(escenario_de_ventas)
        count = 0
        vals_arr = []
        
        for sale in escenario_de_ventas.mapped('sale_id'):
            count=count+1
            total_peiezas = sale.hoja_de_proyecto_origen.total_piezas
            string = 'Sale Number: %s  Aceros: %.2f  Perifericos: %.2f  Otros Prod.: %.2f Otros Gas/Flet/Maq: %.2f Total PZ: %.2f'\
                %(sale.name,sale.hoja_de_proyecto_origen.aceros/total_peiezas,sale.hoja_de_proyecto_origen.perifericos/total_peiezas,sale.hoja_de_proyecto_origen.otros_productos/total_peiezas,sale.hoja_de_proyecto_origen.total_otros_gatos_fletes_y_maquilas/total_peiezas, total_peiezas)
            print(string)
            self.create({
            'sale_id':sale.id, 
            'test_1':sale.hoja_de_proyecto_origen.aceros, 
            'test_2':sale.hoja_de_proyecto_origen.aceros/total_peiezas if total_peiezas != 0 else 0, 

            'test_3':sale.hoja_de_proyecto_origen.perifericos, 
            'test_4':sale.hoja_de_proyecto_origen.perifericos/total_peiezas if total_peiezas != 0 else 0,             
 
            'test_5':sale.hoja_de_proyecto_origen.otros_productos, 
            'test_6':sale.hoja_de_proyecto_origen.otros_productos/total_peiezas if total_peiezas != 0 else 0, 

            'test_7':sale.hoja_de_proyecto_origen.total_otros_gatos_fletes_y_maquilas, 
            'test_8':sale.hoja_de_proyecto_origen.total_otros_gatos_fletes_y_maquilas/sale.hoja_de_proyecto_origen.total_piezas if total_peiezas != 0 else 0, 
    
            'test_9':sale.hoja_de_proyecto_origen.total_piezas, 
            'test_10':sale.hoja_de_proyecto_origen.aceros/sale.hoja_de_proyecto_origen.total_piezas if total_peiezas != 0 else 0, 
        })

from odoo import _, api, fields, models


class FlujoEfectivoDetalle(models.Model):
    _name = 'escenario_de_ventas.flujo_de_efectivo_line'
    _description = 'New Description'
    flujo_de_efectivo = fields.One2many(comodel_name='escenario_de_ventas.flujo_de_efectivo', inverse_name='line_id', string='XXX')
    
    fecha = fields.Date(string='Fecha Esc.Vent.')
    monto_a_pagar = fields.Float(string='Monto TEST')
    
