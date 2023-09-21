from odoo import api, models, _,fields
from odoo.exceptions import UserError
import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, ValidationError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    imagen_de_referencia = fields.Html(string='Imagen de Refencia')
    #x.production_id.bom_id.imagen_de_referencia

    # @api.onchange('product_tmpl_id','product_id')
    # def _onchange_(self):
    #     centros_de_produccions_ids=[]
    #     for x in self.routing_id.operation_ids:
    #         centros_de_produccions_ids.append(x.workcenter_id.id)
        
    #     print(centros_de_produccions_ids)
    #     for work_center_id in centros_de_produccions_ids:

    #         if self.routing_id:
    #             if not self.product_tmpl_id.habilitar_tiempo_de_fabricacion and not self.product_tmpl_id.tiempo_de_fabricacion>0:
    #                 #Ids de pantografo y laser, que funcionan bajo los mismos criterios
    #                 if work_center_id in [13,50]:

    #                     if not self.product_tmpl_id.perimetro > 0:
    #                         raise ValidationError(_(str('El producto\t',self.product_tmpl_id.name,'\t','ID:',self.product_tmpl_id.id,'\t',"No tiene configurado el campo perímetro.")))

    #                     if not self.env['capacidad_de_produccion.calibres_list'].search([('calibre','in',[self.product_tmpl_id.espesor])]):
    #                         raise ValidationError(_('El producto\t',self.product_tmpl_id.name,'\t','ID:',self.product_tmpl_id.id,'\t',"No tiene un espesor válido."))                    
    #                 #Dobladora
    #                 if work_center_id in [17]:
    #                     if not self.product_tmpl_id.dobleces >0:
    #                         raise ValidationError(_('El producto\t',self.product_tmpl_id.name,'\t','ID:',self.product_tmpl_id.id,'\t',"Tiene enrutamiento a Dobladora, pero no tiene la cantidad de dobleces establecida.")) 
    #                 #Cizalla
    #                 if work_center_id in [44]:
    #                     if not self.product_tmpl_id.largo >0:
    #                         raise ValidationError(_('El producto\t',self.product_tmpl_id.name,'\t','ID:',self.product_tmpl_id.id,'\t',"No tiene configurado el largo.")) 
    #                     if not self.product_tmpl_id.alto >0 :
    #                         raise ValidationError(_('El producto\t',self.product_tmpl_id.name,'\t','ID:',self.product_tmpl_id.id,'\t',"No tiene configurado el alto.")) 

    #             elif not self.product_tmpl_id.habilitar_tiempo_de_fabricacion or self.product_tmpl_id.tiempo_de_fabricacion<0:
    #                 raise ValidationError(_('El producto\t',self.product_tmpl_id.name,'\t','ID:',self.product_tmpl_id.id,'\t',"Por favor resise el tiempo de fabricación, no puede ser 0")) 
    #         else:
    #             raise ValidationError(_("Seleccione al menos una ruta")) 


