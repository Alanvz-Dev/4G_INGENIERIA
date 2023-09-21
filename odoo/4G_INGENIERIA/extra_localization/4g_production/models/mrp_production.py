from odoo import fields,api, models, _
from odoo.exceptions import UserError
import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    tiempo_estimado = fields.Float()
    #compute='_compute_tiempo_estimado',string='Tiempo Estimado(Min.)',store=True
    
    @api.depends('production_id')
    def _compute_tiempo_estimado(self):
        for mo in self: 
            # if mo.product_id.id==66650:
            #     print('asfasd')                       
            for workcenter in mo.workcenter_id:
                if workcenter.habilitar_capacidad_de_produccion:
#######################################################################################################################################################################################################################################
                    #Calculos para Pantografo

                    #Verifica si tiene habilitado el check de habilitar capacidad de fabricacion y si es pantografo
                    if workcenter.tipo_de_maquina == 'pantografo' and workcenter.habilitar_capacidad_de_produccion:
                        #Revisa si el producto tiene configurado el tiempo de fabricacion directamente, como es directo ya no se realizan calculos
                        print(mo.product_id.habilitar_tiempo_de_fabricacion)
                        print(type(mo.product_id.habilitar_tiempo_de_fabricacion))
                        
                        if mo.product_id.habilitar_tiempo_de_fabricacion:
                            #mo.product_id.tiempo_de_fabricacion*mo.qty_remaining
                            print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'\t','Cantidad:',mo.qty_remaining,'\t','Tiempo Ingresado:',mo.product_id.tiempo_de_fabricacion,'\t','Tiempo Proporcional:',mo.product_id.tiempo_de_fabricacion*mo.qty_remaining)
                            mo.tiempo_estimado=mo.product_id.tiempo_de_fabricacion*mo.qty_remaining

                        #Si no tiene ingresado un tiempo de fabricacion
                        else:
                            #Varifica que tenga habilitado el check de calcular perimetro
                            if  mo.product_id.calcular_perimetro:
                                #Si lo tiene habilitado el calcular perimetro será alto+largo + 2 para cuadrados y rectangulos unicamente                                
                                tiempo = self.buscar_tiempo_en_tabla_pantografo(mo.product_id,mo.product_id.perimetro) *mo.qty_remaining                                
                                print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'\t','Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.qty_remaining,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                mo.tiempo_estimado=tiempo

                            #Si no tiene habilitado el calcular perimetro se dara por hecho que el perimetro es el que ingreso el usuario en el campo de perimetro
                            elif  mo.product_id.calcular_perimetro==False  and mo.product_id.perimetro >0:
                                #Se calcula el tiempo proporcional en base a la tabla de los centros de produccion por pieza, una vez obtenida se multiplica por la cantidad de piezas                            
                                tiempo = self.buscar_tiempo_en_tabla_pantografo(mo.product_id,mo.product_id.perimetro) *mo.qty_remaining                                
                                print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'\t','Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.qty_remaining,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                mo.tiempo_estimado=tiempo
#######################################################################################################################################################################################################################################                        
#######################################################################################################################################################################################################################################
                    #Calculos para Laser

                    #Verifica si tiene habilitado el check de habilitar capacidad de fabricacion y si es laser
                    if workcenter.tipo_de_maquina == 'laser' and workcenter.habilitar_capacidad_de_produccion:
                        #Revisa si el producto tiene configurado el tiempo de fabricacion directamente, como es directo ya no se realizan calculos
                        if mo.product_id.habilitar_tiempo_de_fabricacion == True:
                            mo.product_id.tiempo_de_fabricacion*mo.qty_remaining
                            #print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'Cantidad:',mo.qty_remaining,'\t','Tiempo Ingresado:',mo.product_id.tiempo_de_fabricacion,'\t','Tiempo Proporcional:',mo.product_id.tiempo_de_fabricacion*mo.qty_remaining)
                            mo.tiempo_estimado=mo.product_id.tiempo_de_fabricacion*mo.qty_remaining

                        #Si no tiene ingresado un tiempo de fabricacion
                        else:
                            #Varifica que tenga habilitado el check de calcular perimetro
                            if  mo.product_id.calcular_perimetro:
                                #Si lo tiene habilitado el calcular perimetro será alto+largo + 2 para cuadrados y rectangulos unicamente                                
                                tiempo = self.buscar_tiempo_en_tabla_laser(mo.product_id,mo.product_id.perimetro) *mo.qty_remaining
                                #print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.qty_remaining,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                mo.tiempo_estimado=tiempo

                            #Si no tiene habilitado el calcular perimetro se dara por hecho que el perimetro es el que ingreso el usuario en el campo de perimetro
                            elif  mo.product_id.calcular_perimetro==False  and mo.product_id.perimetro >0:
                                #Se calcula el tiempo proporcional en base a la tabla de los centros de produccion por pieza, una vez obtenida se multiplica por la cantidad de piezas                            
                                tiempo = self.buscar_tiempo_en_tabla_laser(mo.product_id,mo.product_id.perimetro) *mo.qty_remaining                                
                                #print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.qty_remaining,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                mo.tiempo_estimado=tiempo
#######################################################################################################################################################################################################################################                        
#######################################################################################################################################################################################################################################
                    #Calculos para dobladora

                    #Verifica si tiene habilitado el check de habilitar capacidad de fabricacion y si es laser
                    if workcenter.tipo_de_maquina == 'dobladora' and workcenter.habilitar_capacidad_de_produccion and mo.product_id.dobleces > 0:
                        medida_maxima=max([mo.product_id.alto, mo.product_id.largo])
                        #Revisa si el producto tiene configurado el tiempo de fabricacion directamente, como es directo ya no se realizan calculos
                        if mo.product_id.habilitar_tiempo_de_fabricacion == True:                            
                            #print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'Cantidad:',mo.qty_remaining,'\t','Tiempo Ingresado:',mo.product_id.tiempo_de_fabricacion,'\t','Tiempo Proporcional:',mo.product_id.tiempo_de_fabricacion*mo.qty_remaining)
                            mo.tiempo_estimado=mo.product_id.tiempo_de_fabricacion*mo.qty_remaining*mo.product_id.dobleces

                        #Si no tiene ingresado un tiempo de fabricacion
                        else:
                            #Si no tiene habilitado el calcular perimetro se dara por hecho que el perimetro es el que ingreso el usuario en el campo de perimetro
                            if  mo.product_id.habilitar_tiempo_de_fabricacion == False:
                                #Se calcula el tiempo proporcional en base a la tabla de los centros de produccion por pieza, una vez obtenida se multiplica por la cantidad de piezas                            
                                tiempo = self.buscar_tiempo_en_tabla_dobladora(mo.product_id,medida_maxima) *mo.qty_remaining                                
                                #print('MO:',mo.production_id.name,'\t','Centro de Producción:',workcenter.name,'Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.qty_remaining,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                mo.tiempo_estimado=tiempo
#######################################################################################################################################################################################################################################                        







            
    def buscar_tiempo_en_tabla_pantografo(self,product_product_model,perimetro):
        work_center_pantografo=self.env['mrp.workcenter.pantografo'].search([]) 
        for line in work_center_pantografo:
            if line.calibre_li.calibre <= product_product_model.espesor <= line.calibre_ls.calibre:
                tiempo=perimetro*line.tiempo_de_corte/line.medida_lineal_de_corte
                return tiempo

    def buscar_tiempo_en_tabla_laser(self,product_product_model,perimetro):
        work_center_laser=self.env['mrp.workcenter.laser'].search([]) 
        for line in work_center_laser:
            if line.calibre_li.calibre <= product_product_model.espesor <= line.calibre_ls.calibre:
                tiempo=perimetro*line.tiempo_de_corte/line.medida_lineal_de_corte
                return tiempo

    def buscar_tiempo_en_tabla_dobladora(self,product_product_model,medida_maxima):
        work_center_pantografo=self.env['mrp.workcenter.dobladora'].search([]) 
        for line in work_center_pantografo:
            if line.calibre_li.calibre <= medida_maxima <= line.calibre_ls.calibre:
                tiempo=product_product_model.no_dobleces*line.tiempo_de_corte
                return tiempo


