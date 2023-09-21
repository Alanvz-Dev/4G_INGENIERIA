from odoo import _, api, fields, models
import base64
import random

class CustomBarcode(models.Model):
    _name = 'dining_service.custom_barcode'
    _description = 'Códigos de Barras Temporales'

    profile_picture = fields.Binary(string='Imagen De Perfil')
    name = fields.Char(string='Nombre')
    barcode = fields.Char(string='Código')
    binary = fields.Binary('Binray')
    binary_fname = fields.Char('Binary Name')
    descripcion = fields.Html(string='Descripción')
    numero = fields.Integer(string='No.')
    @api.model
    def create(self, values):
        code = str(random.randint(111111111111, 999999999999))
        nro = str(random.randint(1111, 9999))
        values.update({'barcode':code})
        values.update({'numero':nro})
        barcode = self.env['dining_service.barcode']    
        barcode_image = barcode.generate_barcode(code,values['name']+'.png')
        new_rec =super(CustomBarcode, self).create(values)
        new_rec.binary =base64.b64encode(barcode_image)
        return new_rec


