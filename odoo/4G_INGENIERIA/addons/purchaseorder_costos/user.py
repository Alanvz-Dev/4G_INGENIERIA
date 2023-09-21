from openerp import models, fields, api, _
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from datetime import time, datetime
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _


class res_users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    modify_account_partner=fields.Boolean('Aut. Modifica Factura Proveedor')
