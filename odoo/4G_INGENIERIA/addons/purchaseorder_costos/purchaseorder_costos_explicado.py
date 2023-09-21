# -*- coding: utf-8 -*-

from openerp import models,fields,api,_
from openerp.exceptions import UserError,RedirectWarning,ValidationError

class purchase_order(models.Model):
    _name='purchase.order'
    _inherit='purchase.order'
    apoyo=fields.Boolean('Costo especial')
    categoria_costo=fields.Many2one('categorycost.product','Nombre del producto')
    cost_category=fields.Float('Costo temporal',digits=(14,2))

    @api.onchange('categoria_costo')
    def onchange_precio_categoria(self):
        print "############ self >>>>>>>>> ",self.categoria_costo.cost
        self.cost_category = self.categoria_costo.cost

    @api.multi #(cr, uid, ids, context)
    def update_price_order_list(self):
        ############# CREAR LOS OBJETOS DE SUPPLIER Y PRODUCT
        supplierinfo_obj = self.env['product.supplierinfo']
        #category_obj = self.env['categorycost.product']
        product = self.env['product.template']
        res=0.0
        print "############ self >>>>>>>>> ",self.id
        print "############ self >>>>>>>>> ",self.order_line
        print "############ self >>>>>>>>> ",self._context
        ############# EXTRAER LAS LINEAS DE LA SOLICITUD DE PRESUPUESTO
        for var in self.order_line:
            ################ BUSCAMOS LOS COSTOS DE CADA UNA DE LAS LINEAS PROVENIENTES DE SUPPLIERINFO
            real_supplierinfo_id = supplierinfo_obj.search([('product_tmpl_id','=',var.product_id.id)])
            ################ BISCAMOS LOS PRODUCTOS QUE CORRESPONDAN A LA CATEGORIA SELECCINOADA EN PURCHASE
            real_category_id = product.search([('category_product_id','=',self.categoria_costo.id)])
            print "PRODUCTOS DE LA CATEGORIA ####################",real_category_id
            ############### EXTRAEMOS LOS VALORES DE LOS COSTOS PARA CADA PRODUCTO, RESULTADO DE LA
            ############### BUSQUEDA DE LOS COSTOS EN SUPPLIERINFO
            for var2 in real_supplierinfo_id:
                res=var2.real_price*self.cost_category
            ############### EXTRAEMOS LOS VALORES DE LOS ID DE PRODUCTOS, RESULTADO DE LA
            ############### BUSQUEDA DE LOS IDS EN real_category_id
                for igualacion in real_category_id:
                    ########## VALIDAMOS SI EL EL RESULTADO DE LOS PRODUCTOS CORRESPONDE A ALGUNO
                    ########## DE LOS QUE ESTAN EN LA SOLICITUD DE PRESUPUESTO Y SI ES ASI, SE 
                    ########## REAILZA LA MODIFICACION A ESA SOLICITUD.
                    if var.product_id.id==igualacion.id:
                        var.write({'price_unit':res})
                        print "############ Producto de la lista >>>>>>>>> ",var.product_id.name
                        print "############ Precio original del producto >>>>>>>>> ",var2.real_price
        #supplierinfo = self.env['product.supplierinfo']
        #print "########### SUPPLIERINFO >>> ",supplierinfo
        #default_product_tmpl_id = context['default_product_tmpl_id'] if 'default_product_tmpl_id' in context else False
        lineas = self.order_line.search([('product_id','=',self.id)])
        print "########### LINEAS >>>>>>>> ",lineas
        #product_ids = product.search([('category_product_id','=',self.id)])
        #print "############## PRODUCT IDS >>>>>>>> ",product_ids
        #category_cost = self.cost
        #if product_ids:
        #    for producto in product_ids:
        #        print "########### PRODUCT >>>>>>> ",producto.name
        #        for seller in producto.seller_ids:
        #            seller_real_price = seller.real_price
        #            print "############ SELLER NAME >>> ",seller.name.name
        #            print "############ peso por tramo >> ",seller_real_price
        #            result = category_cost * seller_real_price
        #            print "########## NUEVO PRECIO >>> ",result
        #            seller.write({'price':result})
    #@api.multi
    #def update_price_purchase_order(self):
    #    print "NOMBRE DE LOS PRODUCTOS EN LA LINEA >>>>>>>",self._context

        #res=0.0
        #supplierinfo_obj = self.env['product.supplierinfo']
          #order_lines_obj = self.env['product.order_line']
        #for var in self.order_line:
        #    print "NOMBRE DE LOS PRODUCTOS EN LA LINEA >>>>>>>",var.product_id.name
        #    print "PRECIO UNITARIOS DE LOS PRODUCTOS EN LA LINEA >>>>>>>",var.price_unit
        #    res=var.price_unit*self.cost_category
        #    print "RESULTADO DE LOS PRODUCTOS EN LA LINEA >>>>>>>",res
        #    var.write({'price_unit':res})
        #    print "#############################################################"



#           real_supplierinfo_id=supplierinfo_obj.search([('product_tmpl_id','=',var.product_id.id)])
#            template_id = self.env['product.template']
#            product_template_id=template_id.search([('id','=',var.product_id.id)])
#            print ">>>>>>CATEGORIA PRODUCTO >>>>>",product_template_id
#            print ">>>>>>CATEGORIA SELECCIONADA >>>>>",self.categoria_costo.name
#            if self.apoyo==True:
#                res=0.0
#                for valores in real_supplierinfo_id:                    
                    #template_id2 = self.env['purchase.order.line']
                    #purchase_lines = template_id2
                    
                    
#                    res=valores.real_price*self.cost_category
#                    print ">>>>>>>>>>>>>>>>>>>>>>> Linea de supplier >>>>>",valores.real_price
#                    print ">>>>>>>>>>>>>>>>>>>>>>> Categorias de costos >>>>>",self.cost_category
 #                   print ">>>>>>PRICE UNIT>>>>>",var.price_unit
 #                   print ">>>>>>RESULTADO >>>>>",res
 #                   #print ">>>>>>RESULTADO >>>>>",template_id2.price_unit
 #                   var.write({'price_unit':res})
 #           else:
 #               print ">>>>>>>>>>>>>>>>>>>>>>> no paso el if >>>>>"


    #@api.multi
    #def _add_supplier_to_product(self):
        #print ">>>>>>ONCHANGE PRUEBAS >>>>>>>>>>",self.order_line.product_id.name
        #costoo = 5.00
        #self.order_line.product_id.write({'price_unit':costoo})