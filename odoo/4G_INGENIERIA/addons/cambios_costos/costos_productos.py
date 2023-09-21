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
        supplierinfo = self.env['product.supplierinfo']
        product = self.env['product.template']
        product_ids = product.search([('category_product_id','=',self.id)])
        category_cost = self.cost
        if product_ids:
            for producto in product_ids:
                for seller in producto.seller_ids:
                    seller_real_price = seller.real_price
                    result = category_cost * seller_real_price
                    seller.write({'price':result})


    @api.multi
    def show_data_report_account_invoice(self):

        #move_lines_purchase_order_obj = self.env['purchase.order.line']
        #report = move_lines_purchase_order_obj.search([('account_analytic_id','=',self.account_analytic_account_id.id)])
        #print "VALOREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES DEL OBJETO",report
        #report_array = []
        #for data_report in report:
        #    print "VALOREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES",data_report
        #    report_array.append(data_report)
        #return report_array

        self.env.cr.execute("""
            select account_invoice.move_name, res_partner.name, account_invoice.date_invoice, account_invoice.date_due, sale_order.no_compra_cliente, account_invoice.amount_total, account_invoice.state, res_users.login from account_invoice left join res_partner on account_invoice.partner_id=res_partner.id left join res_users on account_invoice.user_id=res_users.id left join sale_order on account_invoice.origin=sale_order.name where move_name LIKE '%FA%' order by move_name;
            """)
        report_details=self.env.cr.fetchall()
        report_array = []
        for valores in report_details:
            report_array.append(valores)
        return report_array


    @api.multi
    def print_report_account_invoice(self):

        return self.env['report'].get_action(self,'cambios_costos.template_accountinvoice_report')



class product_template(models.Model):
    _name='product.template'
    _inherit='product.template'
    _description='Agregar categorias de productos'
    _defaults={
        'active':False,
        'uom_id':0,
        'uom_po_id':0
    }

    category_product_id=fields.Many2one('categorycost.product',string='Categoria del producto')
    
    @api.onchange('category_product_id')
    def onchange_real_product_seller(self):
        if self.category_product_id:
            cost = self.category_product_id.cost
            if self.seller_ids:
                for seller in self.seller_ids:
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
        

        context = self._context
        default_product_tmpl_id = context['default_product_tmpl_id'] if 'default_product_tmpl_id' in context else False
        product_br = self.env['product.template'].browse(default_product_tmpl_id)
        cost = 1.0
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