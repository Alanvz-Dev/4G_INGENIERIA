# -*- coding: utf-8 -*-


from odoo import models, fields, api

class costos_acero(models.Model):
    _name = 'costos_acero.costos_acero'
    _rec_name = 'id'



    categrory = fields.Many2many('product.category', string='Categoría')
    new_value = fields.Float(string='Nuevo Valor')
    categrory_str=fields.Char('Categorías')


    @api.model
    def create(self,vals):
        
        
        products=self.env['product.template'].search([('categ_id','in',vals['categrory'][0][2])])
        vals['categrory_str']=products.mapped('categ_id.complete_name')
        print(products.mapped('categ_id.complete_name'))
        print(vals['categrory_str'])
        for product in products:
            try:
                product.standard_price=product.weight*vals['new_value']
                product.cost_product=product.weight*vals['new_value']
            except:
                print('Error')            
            try:
                product.standard_price=product.weight*vals['new_value']
            except:
                print('Error')
        
        print(products)

        return super(costos_acero, self).create(vals)
        
