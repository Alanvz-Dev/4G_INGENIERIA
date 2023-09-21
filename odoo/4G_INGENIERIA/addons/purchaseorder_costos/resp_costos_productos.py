# -*- coding: utf-8 -*-

from openerp import models,fields,api,_
from openerp.exceptions import UserError,RedirectWarning,ValidationError

class categorycost_product(models.Model):
    _name='categorycost.product'
    _description='Categoria de precios del producto'
    name=fields.Char('Nombre de categoria',size=128, required=True)
    cost=fields.Float('Costo de categoria',digits=(14,2), required=True)

# Environment
# Funciones del ORM
# Create
# Write
# Unlink
# Read
# Browse
# Search

    @api.multi #(cr, uid, ids, context)
    def update_costs_supplierinfo(self):
        print "############ self >>>>>>>>> ",self.ids
        print "############ self >>>>>>>>> ",self._context
        supplierinfo = self.env['product.supplierinfo']
        print "########### SUPPLIERINFO >>> ",supplierinfo
        product = self.env['product.template']
        print "########### product >>>>>>>> ",product
        product_ids = product.search([('category_product_id','=',self.id)])
        print "############## PRODUCT IDS >>>>>>>> ",product_ids
        category_cost = self.cost
        if product_ids:
            for producto in product_ids:
                print "########### PRODUCT >>>>>>> ",producto.name
                for seller in producto.seller_ids:
                    seller_real_price = seller.real_price
                    print "############ SELLER NAME >>> ",seller.name.name
                    print "############ peso por tramo >> ",seller_real_price
                    result = category_cost * seller_real_price
                    print "########## NUEVO PRECIO >>> ",result
                    seller.write({'price':result})

class product_template(models.Model):
    _name='product.template'
    _inherit='product.template'
    _description='Agregar categorias de productos'

    category_product_id=fields.Many2one('categorycost.product','Categoria del producto')
    
    @api.onchange('category_product_id')
    def onchange_real_product_seller(self):
        print "############### id de la categoria",self.category_product_id
        if self.category_product_id:
            cost = self.category_product_id.cost
            print "############### costo de la categoria",self.category_product_id.cost
            if self.seller_ids:
                for seller in self.seller_ids:
                    print "############ SELLER NAME >>> ", seller.name.name
                    seller_real_price = seller.real_price
                    result = cost * seller_real_price
                    seller.write({'price':result})

class product_supplierinfo(models.Model):
    _name='product.supplierinfo'
    _inherit='product.supplierinfo'
    _description='Agregar categorias de productos'
#    price=fields.Float(readonly=True)
    real_price=fields.Float('Peso por tramo',digits=(14,3),required=True)   
    _defaults={
        'real_price':'1.0',
    }

    @api.onchange('real_price')
    def onchange_real_product(self):
#        print "----------Esto es un Onchange####################"
 #       var = self.env['account.analytic.account']
  #      var_ids = var.search([('id','=',5)])
   #     print "------------------------------>>>>",var_ids
    #    for campos in var_ids:
     #       print "nombre de la cuenta analitica--------------------->",campos.name
      #  var2 = self.env['crossovered.budget.lines']
       # var2_ids = var2.search([('analytic_account_id','=',campos.id)])
        #    #for cuentas2 in var2_ids.crossovered_budget_line:
#        print "CUENTAS--------------------->",var2_ids
 #       for lineas in var2_ids:
  #          print "----------------costo",lineas.planned_amount
   #         print "----------------costo real",lineas.practical_amount
    #    var3 = self.env['account.invoice.line']

        #var4 = var3.search([('id')])
     #   for campos2 in var3:
      #      print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>campos",campos2.account_analytic_id



   #     var2=var._context
  #      var3= var2['uid']
 #       var4 = self.env['res.users'].browse(var3)
#        name_usr=var4.name
#       print "------------------------------>>>>",var4.name
#         if name_usr=='Administrator':
#            print "----------Esto es un Onchange Admin####################"
#             #precio=fields.Float(readonly=True)
#             #self.price=precio
#         else:
#             print "----------Esto es un Onchange USR####################"
#             #precio=fields.Float(readonly=False)
#             #self.price=precio
#        var3=var2[]
        
        print "################# CONTEXT >>>> ",self._context
        context = self._context
        default_product_tmpl_id = context['default_product_tmpl_id'] if 'default_product_tmpl_id' in context else False
        product_br = self.env['product.template'].browse(default_product_tmpl_id)
        cost = 1.0
        print "Costo de la caterogia german #########################",product_br
        print "Costo de la caterogia #########################",product_br.category_product_id.cost
        if product_br.category_product_id:
            cost = product_br.category_product_id.cost
            result = cost * self.real_price
            self.price = result
        else:
            result = self.real_price * 1
            self.price = result
        # self.env.cr.execute(""" 
        #     SELECT cost FROM categorycost_product 
        #         WHERE id = 1; """)
        # my_id=self.env.cr.fetchall()[0]
        # total=0.0
        # total=self.real_price*my_id[0]
        # self.price = total      


















#   @api.onchange('real_price')
#   def onchange_real_product(self, cr, uid, ids, context=None):
#       print "----------Esto es un Onchange####################"
#       print "---------------===============",self.real_price

#       calificaciones_list=[]
#       print "-------->>>>",self.grado_id.materia_ids
#       for materia in self.grado_id.materia_ids:
#           xvals=(0,0,{
#                   'name':materia.materia_id.id,
#                   'calificacion':5
#               })
#           calificaciones_list.append(xvals)
#       self.update({'calificaciones_ids':calificaciones_list})

        #print self.grado_id



#class categorycost_product(models.Model):
#   _name='categorycost.product'
#   _description='Categoria de precios del producto'
#   name=fields.Char('Nombre de categoria',size=128, required=True)
#   cost=fields.Float('Costo de categoria',digits=(14,2), required=True)


#   @api.multi
#   def _get_school_default(self):
#       partner_obj=self.env['res.partner']
#       school_id=partner_obj.search([('name','=','Escuela Principal'),('company_type','=','is_school')])
#       if school_id:
#           return school_id
#       else:
#           raise ValidationError(_('El Registro de Escuela Principal no Existe. Dar de alta la escuela en Clientes'))

#   ptr=fields.Float('PTR',digits=(14,2))
#   angulo=fields.Float('Angulo',digits=(14,2))
#   canal=fields.Float('Canal',digits=(14,2))
#   laminaplaca=fields.Float('Lamina/Placa',digits=(14,2))
#   redondo=fields.Float('Redondo',digits=(14,2))
#   ipr=fields.Float('IPR',digits=(14,2))
#   solera=fields.Float('Solera',digits=(14,2))
#   laminafria=fields.Float('Lamina/Fria',digits=(14,2))
#   tubo=fields.Float('Tubo',digits=(14,2))

#   destino_entrega=fields.integer("Destino de Factura",required=True)

#   @api.multi
#   def _get_account_invoice_contact(self):
#       partner_obj=self.env['res.partner']
#       school_id=partner_obj.search([('name','=','Escuela Principal'),('company_type','=','is_school')])
#       if school_id:
#           return school_id
#       else:
#           raise ValidationError(_('El Registro de Escuela Principal no Existe. Dar de alta la escuela en Clientes'))