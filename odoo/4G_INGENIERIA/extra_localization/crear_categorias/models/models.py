from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def create(self, values):
        if self._compute_is_group_crear_categorias():
            res = super(ProductCategory, self).create(values)
            # here you can do accordingly
            return res
        else:
            raise ValidationError("No tienes Permisos para realizar esta operación.")



    
    def _compute_is_group_crear_categorias(self):
        return self.env['res.users'].has_group('crear_categorias.group_crear_categorias')