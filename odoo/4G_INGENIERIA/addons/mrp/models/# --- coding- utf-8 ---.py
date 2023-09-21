# -*- coding: utf-8 -*-
mrp_bom = self.env['mrp.bom']
mrp_bom_lines = self.env['mrp.bom.line']
product_product = self.env['product.product']

def search_lines(self,bom_id):
    return mrp_bom_lines.search([('bom_id','=',bom_id)])


head_line = search_lines(self,1630)


def determine_ldm(self):
    for line in head_line:
        if line.product_id._compute_bom_count:
            print('Tiene Lista de Materiales')
        else:
            print('No tiene lista de Materiales')


        

    



