# -*- coding: utf-8 -*-


from odoo import api, fields, models, _



class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit ='mrp.production'

    analytic_account_id = fields.Many2one('account.analytic.account','Cuenta Analitica')
    quotation_request_create = fields.Boolean('Solicitud Creada', copy=False)
    quotation_id = fields.Many2one('purchase.order', 'Presupuesto', copy=False)
    quotation_name_list = fields.Char('Presupuestos', size=512, copy=False)


    @api.v7
    def product_id_change(self, cr, uid, ids, product_id, product_qty, context=None):
        res = super(MrpProduction, self).product_id_change(cr, uid, ids, product_id, product_qty, context)
        if product_id:
            product_br = self.pool.get('product.product').browse(cr, uid, product_id, context)
            if product_br.analytic_account_id:
                res['value'].update({'analytic_account_id': product_br.analytic_account_id.id})
        return res





