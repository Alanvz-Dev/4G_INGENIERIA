from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product'

    
    tiempo_de_fabricacion = fields.Float(string='Tiempo de Fabricación(Min.)',digits=(2,2))
    perimetro = fields.Float(string='Perímetro(mm)',digits=(4,4))
    alto = fields.Float(string='Alto (mm)', digits=(4, 4),help="Alto usado para cálculo de capacidad de producción expresado en milimetros")
    largo = fields.Float(string='Largo (mm)', digits=(4, 4),help="Largo usado para cálculo de capacidad de producción expresado en milimetros")
    espesor = fields.Float(string='Espesor(mm)',digits=(4,4))
    dobleces = fields.Float(string='Dobleces (No.)', digits=(1, 1),help="Número de Dobleces de la pieza")
    calcular_perimetro = fields.Boolean(string='Calcular Perímetro',default=False)
    habilitar_tiempo_de_fabricacion = fields.Boolean(string='Ingresar Tiempo de Fabricación',default=False)
    

    @api.constrains('alto','largo','calcular_perimetro')
    def _constrains_fieldname(self):
        if self.calcular_perimetro==False and self.alto > 0 and self.largo >0 and self.perimetro>0:
            raise ValidationError("Tiene valores asignados en largo y alto, por favor establesca a 0 o habilite calcular perímetro ")
        if self.calcular_perimetro==True and self.alto > 0 and self.largo >0:
            self.perimetro=(self.alto+self.largo)*2
        
            
    
