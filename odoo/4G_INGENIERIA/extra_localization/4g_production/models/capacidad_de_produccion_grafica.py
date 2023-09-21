from ast import excepthandler
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class CalibresValidos2(models.Model):
    _name = "capacidad_de_produccion.calibres_list"
    _rec_name='calibre'
    calibre = fields.Float(string='Espesor(mm)',digits=(4,4))

class MedidasMaximas(models.Model):
    _name = "capacidad_de_produccion.madida_maxima"
    _rec_name='medida_maxima'
    medida_maxima = fields.Float(string='Medida Máxima(mm)',digits=(4,4))


class CalibresValidos2(models.Model):
    _name = "capacidad_de_produccion.dia_det"
    mo = fields.Many2one('mrp.production')
    producto = fields.Many2one('product.product')
    centro_de_produccion = fields.Many2one('mrp.workcenter')
    tiempo_estimado = fields.Float()
    vigente_desde = fields.Datetime()
    dia = fields.Datetime()
    




class CalibresValidos(models.Model):
    _name = "capacidad_de_produccion.dia"
    _rec_name='centro_de_produccion'
    dia = fields.Datetime(string='Día')
    centro_de_produccion = fields.Many2one('mrp.workcenter')
    
    @api.onchange('dia')
    def _onchange_dia(self):
        for item in self.mos:
            item.vigente_desde=self.dia
            for mo in item.mo:
                mo.date_planned_start=self.dia



    

    mos = fields.Many2many('capacidad_de_produccion.grafica', string="MO's")
    
    
    tiempo_estimado = fields.Float(string="Tiempo De Operación Estimado (Min.)")

    capacidad_instalada = fields.Float(compute='_compute_capacidad_instalada',string='Capacidad Instalada(Min.)',digits=(2,2),store=True)
    @api.depends('centro_de_produccion')
    def _compute_capacidad_instalada(self):
        for item in self:
            item.capacidad_instalada=item.centro_de_produccion.capacity - item.centro_de_produccion.time_start - item.centro_de_produccion.time_stop
        

    capacidad_disponible = fields.Float(compute='_compute_capacidad_disponible',string='Capacidad Disponible(Min.)',digits=(2,2),store=True)
    @api.depends('centro_de_produccion')
    def _compute_capacidad_disponible(self):
        for item in self:
            item.capacidad_disponible=item.capacidad_instalada-item.tiempo_estimado
        

    @api.multi
    def fill_graph_data(self):
        x = self.env['capacidad_de_produccion.grafica'].return_views()
        if x:
            return {
                'name': 'MOs erróneas para la capacidad de producción',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mrp.production',
                'domain': [('id', 'in', x)],
            }
        views = [
                 (self.env.ref('mrp.mrp_capacidad_piv_dia').id, 'pivot'),
                #  (self.env.ref('mrp.mrp_capacidad_dia').id, 'graph'),
                 (self.env.ref('mrp.mrp_capacidad_list_dia').id, 'list'),
                 (self.env.ref('mrp.mrp_capacidad_prod_view_form_dia').id, 'form')]
        return{
                'name': 'Capacidad de Producción',
                'view_type': 'form',
                "view_mode": "pivot,tree,form",
                #"view_mode": "tree,form,graph",
                'view_id': False,
                "res_model": "capacidad_de_produccion.dia",
                'views': views,
                #'domain': [('id', 'in', invoices.ids)],
                'type': 'ir.actions.act_window',
            }

    

class CalibresValidos(models.Model):
    _name = "capacidad_de_produccion.mes"
    mes = fields.Float(string='Mes')
    centro_de_produccion = fields.Many2one('mrp.workcenter')
    capacidad_instalada = fields.Float(string='Capacidad Instalada')
    capacidad_disponible = fields.Float(string='Capacidad Disponible')
    horas_capacidad_instalada = fields.Float()
    horas_capacidad_disponible = fields.Float()
    
    




class CapacidadDeProduccion(models.Model):
    _name = "capacidad_de_produccion.grafica"
    _rec_name = "centro_de_produccion"
    producto = fields.Many2one('product.product')
    centro_de_produccion = fields.Many2one('mrp.workcenter')
    mo = fields.Many2one('mrp.production')
    tiempo_estimado = fields.Float(string="Tiempo De Operación Estimado (Min.)")
    vigente_desde = fields.Datetime(store=True,related='mo.date_planned_start')
    piezas = fields.Float(store=True,related='mo.product_qty',string="Piezas")
    
    


    
    @api.multi
    def return_views(self):
        return self.fill_graph_data()



    def get_mo_hijo(self):
        return self.env['mrp.production'].search([('origin', 'not like', 'SO%'), ('state', 'not in', [
                                                           'done', 'cancel']), ('routing_id', 'not in', [47, 112, 113, 114, 115, 116, 37]), ('routing_id', '!=', False)])
    def eliminar_registros_existentes(self):
        record_set = self.env['capacidad_de_produccion.grafica'].search([])
        record_set.unlink()   
        record_set = self.env['capacidad_de_produccion.dia'].search([])
        record_set.unlink() 

    @api.multi
    def fill_graph_data(self):
        self.eliminar_registros_existentes()
        mo_ids_err = []
        for mo in self.get_mo_hijo():
            try:
                if mo.name=='MO/50053':
                    print('Revisar')        
                for workcenter in mo.routing_id.operation_ids:
                    tiempo_estimado=0.0
                    capacidad_de_produccion_vals = {}
                    if workcenter.workcenter_id.habilitar_capacidad_de_produccion:
############    ###########################################################################################################################################################################################################################
                        #Calculos para Pantografo

                        #Verifica si tiene habilitado el check de habilitar capacidad de fabricacion y si es pantografo
                        if workcenter.workcenter_id.tipo_de_maquina == 'pantografo' and workcenter.workcenter_id.habilitar_capacidad_de_produccion:
                            #Revisa si el producto tiene configurado el tiempo de fabricacion directamente, como es directo ya no se realizan calculos
                            #print(mo.product_id.habilitar_tiempo_de_fabricacion)
                            #print(type(mo.product_id.habilitar_tiempo_de_fabricacion))

                            if mo.product_id.habilitar_tiempo_de_fabricacion:
                                #mo.product_id.tiempo_de_fabricacion*mo.product_qty
                                #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'\t','Cantidad:',mo.product_qty,'\t','Tiempo Ingresado:',mo.product_id.tiempo_de_fabricacion,'\t','Tiempo Proporcional:',mo.product_id.tiempo_de_fabricacion*mo.product_qty)
                                tiempo_estimado=mo.product_id.tiempo_de_fabricacion*mo.product_qty

                            #Si no tiene ingresado un tiempo de fabricacion
                            else:
                                if mo.product_id.id == 65996:
                                    print("ERR -->")
                                #Varifica que tenga habilitado el check de calcular perimetro                            
                                if not mo.product_id:
                                    raise UserError('No tiene configurada la cantidad de producto en la MO\t'+str(mo.id)+' '+mo.product_qty)                                

                                if  mo.product_id.calcular_perimetro:
                                    if not mo.product_id.perimetro:
                                        raise UserError('No tiene configurado el campo perimetro en el producto\t'+str(mo.product_id.id)+' '+mo.product_id.name)
                                    if not mo.product_qty:
                                        raise UserError('No tiene configurada la cantidad de producto en la MO\t'+str(mo.id)+' '+mo.product_qty)


                                    #Si lo tiene habilitado el calcular perimetro será alto+largo + 2 para cuadrados y rectangulos unicamente                                
                                    tiempo = self.buscar_tiempo_en_tabla_pantografo(mo.product_id,mo.product_id.perimetro) *mo.product_qty                                
                                    #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'\t','Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.product_qty,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                    tiempo_estimado=tiempo

                                #Si no tiene habilitado el calcular perimetro se dara por hecho que el perimetro es el que ingreso el usuario en el campo de perimetro

                                elif  mo.product_id.calcular_perimetro==False  and mo.product_id.perimetro >0:

                                    try:
                                        if not mo.product_id.perimetro:
                                            raise UserError('No tiene configurado el campo perimetro en el producto\t'+str(mo.product_id.id)+' '+mo.product_id.name)
                                        if not mo.product_qty:
                                            raise UserError('No tiene configurada la cantidad de producto en la MO\t'+str(mo.id)+' '+mo.product_qty)                                    
                                            #Se calcula el tiempo proporcional en base a la tabla de los centros de produccion por pieza, una vez obtenida se multiplica por la cantidad de piezas                            
                                        tiempo = self.buscar_tiempo_en_tabla_pantografo(mo.product_id,mo.product_id.perimetro) *mo.product_qty                                
                                        #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'\t','Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.product_qty,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                        tiempo_estimado=tiempo
                                    except:                                    
                                        tiempo=0
############    ###########################################################################################################################################################################################################################                        
############    ###########################################################################################################################################################################################################################
                        #Calculos para Laser

                        #Verifica si tiene habilitado el check de habilitar capacidad de fabricacion y si es laser
                        if workcenter.workcenter_id.tipo_de_maquina == 'laser' and workcenter.workcenter_id.habilitar_capacidad_de_produccion:
                            #Revisa si el producto tiene configurado el tiempo de fabricacion directamente, como es directo ya no se realizan calculos
                            if mo.product_id.habilitar_tiempo_de_fabricacion == True:
                                mo.product_id.tiempo_de_fabricacion*mo.product_qty
                                #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'Cantidad:',mo.product_qty,'\t','Tiempo Ingresado:',mo.product_id.tiempo_de_fabricacion,'\t','Tiempo Proporcional:',mo.product_id.tiempo_de_fabricacion*mo.product_qty)
                                tiempo_estimado=mo.product_id.tiempo_de_fabricacion*mo.product_qty

                            #Si no tiene ingresado un tiempo de fabricacion
                            else:
                                #Varifica que tenga habilitado el check de calcular perimetro
                                if  mo.product_id.calcular_perimetro:
                                    if not mo.product_id.perimetro:
                                        raise UserError('No tiene configurado el campo perimetro en el producto\t'+str(mo.product_id.id)+' '+mo.product_id.name)
                                    if not mo.product_qty:
                                        raise UserError('No tiene configurada la cantidad de producto en la MO\t'+str(mo.id)+' '+mo.product_qty)                                      
                                    #Si lo tiene habilitado el calcular perimetro será alto+largo + 2 para cuadrados y rectangulos unicamente                                
                                    tiempo = self.buscar_tiempo_en_tabla_laser(mo.product_id,mo.product_id.perimetro) *mo.product_qty
                                    #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.product_qty,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                    tiempo_estimado=tiempo

                                #Si no tiene habilitado el calcular perimetro se dara por hecho que el perimetro es el que ingreso el usuario en el campo de perimetro
                                elif  mo.product_id.calcular_perimetro==False  and mo.product_id.perimetro >0:
                                    #Se calcula el tiempo proporcional en base a la tabla de los centros de produccion por pieza, una vez obtenida se multiplica por la cantidad de piezas                            

                                    try:
                                        if not mo.product_id.perimetro:
                                            raise UserError('No tiene configurado el campo perimetro en el producto\t'+str(mo.product_id.id)+' '+mo.product_id.name)
                                        if not mo.product_qty:
                                            raise UserError('No tiene configurada la cantidad de producto en la MO\t'+str(mo.id)+' '+mo.product_qty)                                          
                                        tiempo = self.buscar_tiempo_en_tabla_laser(mo.product_id,mo.product_id.perimetro) *mo.product_qty                                
                                        #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.product_qty,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                    except:
                                        tiempo=0
                                    tiempo_estimado=tiempo
############    ###########################################################################################################################################################################################################################                        
############    ###########################################################################################################################################################################################################################
                        #Calculos para dobladora

                        #Verifica si tiene habilitado el check de habilitar capacidad de fabricacion y si es laser
                        if workcenter.workcenter_id.tipo_de_maquina == 'dobladora' and workcenter.workcenter_id.habilitar_capacidad_de_produccion and mo.product_id.dobleces > 0:
                            # if mo.name=='MO/50050':
                            #     print('') 
                            medida_maxima=max([mo.product_id.alto, mo.product_id.largo])
                            #Revisa si el producto tiene configurado el tiempo de fabricacion directamente, como es directo ya no se realizan calculos
                            if mo.product_id.habilitar_tiempo_de_fabricacion == True:                            
                                #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'Cantidad:',mo.product_qty,'\t','Tiempo Ingresado:',mo.product_id.tiempo_de_fabricacion,'\t','Tiempo Proporcional:',mo.product_id.tiempo_de_fabricacion*mo.product_qty)
                                tiempo_estimado=mo.product_id.tiempo_de_fabricacion*mo.product_qty*mo.product_id.dobleces

                            #Si no tiene ingresado un tiempo de fabricacion
                            else:
                                #Si no tiene habilitado el calcular perimetro se dara por hecho que el perimetro es el que ingreso el usuario en el campo de perimetro
                                if  mo.product_id.habilitar_tiempo_de_fabricacion == False:
                                    #Se calcula el tiempo proporcional en base a la tabla de los centros de produccion por pieza, una vez obtenida se multiplica por la cantidad de piezas                            
                                    if not mo.product_id.perimetro:
                                        raise UserError('No tiene configurado el campo perimetro en el producto\t'+str(mo.product_id.id)+' '+mo.product_id.name)
                                    if not mo.product_qty:
                                        raise UserError('No tiene configurada la cantidad de producto en la MO\t'+str(mo.id)+' '+mo.product_qty)                                      
                                    tiempo = self.buscar_tiempo_en_tabla_dobladora(mo.product_id) *mo.product_qty                                
                                    #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.product_qty,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                    tiempo_estimado=tiempo
############    ###########################################################################################################################################################################################################################                        
############    ###########################################################################################################################################################################################################################
                        #Calculos para cizalla
                        # print(workcenter.workcenter_id.tipo_de_maquina)
                        #Verifica si tiene habilitado el check de habilitar capacidad de fabricacion y si es laser
                        if workcenter.workcenter_id.tipo_de_maquina == 'cizalla' and workcenter.workcenter_id.habilitar_capacidad_de_produccion:
                            medida_maxima=max([mo.product_id.alto, mo.product_id.largo])
                            #Revisa si el producto tiene configurado el tiempo de fabricacion directamente, como es directo ya no se realizan calculos
                            if mo.product_id.habilitar_tiempo_de_fabricacion == True:                            
                                #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'Cantidad:',mo.product_qty,'\t','Tiempo Ingresado:',mo.product_id.tiempo_de_fabricacion,'\t','Tiempo Proporcional:',mo.product_id.tiempo_de_fabricacion*mo.product_qty)
                                tiempo_estimado=mo.product_id.tiempo_de_fabricacion*mo.product_qty

                            #Si no tiene ingresado un tiempo de fabricacion
                            elif mo.product_id.habilitar_tiempo_de_fabricacion == False:
                                #Si no tiene habilitado el calcular perimetro se dara por hecho que el perimetro es el que ingreso el usuario en el campo de perimetro

                                    #Se calcula el tiempo proporcional en base a la tabla de los centros de produccion por pieza, una vez obtenida se multiplica por la cantidad de piezas                            
                                    y= self.buscar_tiempo_en_tabla_cizalla(mo.product_id.espesor) or 0
                                    z=mo.product_qty
                                    try:
                                        tiempo = y*z                              
                                    except:
                                        tiempo = self.buscar_tiempo_en_tabla_cizalla(mo.product_id.espesor) * (mo.product_qty) 
                                    #print('MO:',mo.name,'\t','Centro de Producción:',workcenter.workcenter_id.name,'Espesor',mo.product_id.espesor,'\t','Cantidad:',mo.product_qty,'\t','Perimetro:',mo.product_id.perimetro,'\t','Tiempo Proporcional:',tiempo)
                                    tiempo_estimado=tiempo
############    ###########################################################################################################################################################################################################################                        
                    capacidad_de_produccion_vals.update({'producto': mo.product_id.id,
                    'mo': mo.id,
                    'centro_de_produccion': workcenter.workcenter_id.id,
                    'tiempo_estimado':tiempo_estimado})
                    #print(capacidad_de_produccion_vals)
                    self.validate_and_create(capacidad_de_produccion_vals)
            except:
                mo_ids_err.append(mo.id)
                print(mo.id)
                # raise UserError('Error en MO: %s %s , Producto : %s %s'%(mo.id,mo.name,str(mo.product_id.id),mo.product_id.name))
        print(mo_ids_err)
        if len(mo_ids_err)>0:
            return mo_ids_err  

       
        ##Agrupar y llenar tabla de centro de producción
        self.env.cr.execute("select DATE(vigente_desde) as dia,sum(tiempo_estimado) as tiempo_estimado ,centro_de_produccion from capacidad_de_produccion_grafica group by dia,centro_de_produccion")
        result=self.env.cr.dictfetchall()
        for item in result:
            #print("select mo,producto,centro_de_produccion,tiempo_estimado,vigente_desde ,dia  from(select DATE(vigente_desde) as dia,* from capacidad_de_produccion_grafica) as tabla where dia ='"+str(item.get('dia'))+"' and centro_de_produccion =="+str(item.get('centro_de_produccion'))+"")
            self.env.cr.execute("select id,mo,producto,centro_de_produccion,tiempo_estimado ,dia  from(select DATE(vigente_desde) as dia,* from capacidad_de_produccion_grafica) as tabla where dia ='"+str(item.get('dia'))+"' and centro_de_produccion ="+str(item.get('centro_de_produccion'))+"")
            mo_ids = self.env.cr.dictfetchall()
            mo_ids_arr=[]
            for item_mo in mo_ids:
                mo_ids_arr.append(item_mo.get('id'))
                item.update({'mos':[(6, 0, mo_ids_arr)]})
            self.env['capacidad_de_produccion.dia'].create(item)



            
    def buscar_tiempo_en_tabla_pantografo(self,product_product_model,perimetro):
        tiempo=0
        if perimetro>0.0:
            work_center_pantografo=self.env['mrp.workcenter.pantografo'].search([]) 
            for line in work_center_pantografo:
                try:                    
                    if line.calibre_li.calibre and product_product_model.espesor and line.calibre_ls.calibre:    
                        if round(product_product_model.espesor, 4) >= line.calibre_li.calibre and  round(product_product_model.espesor, 4) <= line.calibre_ls.calibre:
                            tiempo=perimetro*line.tiempo_de_corte/line.medida_lineal_de_corte/1000
                        return tiempo                        
                except:
                    print('Error')
        else: return 0.0                    

    def buscar_tiempo_en_tabla_laser(self,product_product_model,perimetro):
        tiempo=0
        if perimetro>0.0:        
            work_center_laser=self.env['mrp.workcenter.laser'].search([]) 
            for line in work_center_laser:
                if line.calibre_li.calibre and product_product_model.espesor and line.calibre_ls.calibre:    
                    if round(product_product_model.espesor, 4) >=line.calibre_li.calibre and round(product_product_model.espesor, 4) <= line.calibre_ls.calibre:
                        tiempo=perimetro*line.tiempo_de_corte/line.medida_lineal_de_corte/1000
            return tiempo
        else: return 0.0                    

    def buscar_tiempo_en_tabla_dobladora(self,product_product_model):
        #print(product_product_model.dobleces)
        #print(product_product_model.espesor)
        tiempo=0
        if product_product_model.espesor >0.0:                    
            work_center_pantografo=self.env['mrp.workcenter.dobladora'].search([]) 
            for line in work_center_pantografo:
                #print(line.calibre_li.calibre)
                #print(line.calibre_ls.calibre)
                #print('\n')
                if (round(product_product_model.espesor, 4) >=line.calibre_li.calibre and round(product_product_model.espesor, 4) <= line.calibre_ls.calibre):
                    tiempo=product_product_model.dobleces*line.tiempo_de_corte
                    return tiempo 
        else: return 0.0                    

    def buscar_tiempo_en_tabla_cizalla(self,medida_maxima_espesor):
        tiempo=0
        if medida_maxima_espesor>0.0:                            
            work_center_cizalla=self.env['mrp.workcenter.cizalla'].search([]) 
            for line in work_center_cizalla:
                if (round(medida_maxima_espesor, 4) >=line.calibre_li.calibre and round(medida_maxima_espesor, 4) <= line.calibre_ls.calibre):
                    tiempo=line.tiempo_de_corte
                    return tiempo
        else: return 0.0


    def validate_and_create(self,capacidad_de_produccion_vals):
        if 'centro_de_produccion' in capacidad_de_produccion_vals and 'producto' in capacidad_de_produccion_vals and 'tiempo_estimado' in capacidad_de_produccion_vals and 'mo' in capacidad_de_produccion_vals and int(capacidad_de_produccion_vals.get('tiempo_estimado')) >0.0:
            try:
                self.env['capacidad_de_produccion.grafica'].create(
                capacidad_de_produccion_vals)
            except:
                print('')