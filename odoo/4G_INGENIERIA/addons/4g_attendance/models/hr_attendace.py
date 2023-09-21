# -*- coding: utf-8 -*-

from odoo import fields, models, api 
from odoo.exceptions import UserError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import datetime
import logging
_logger = logging.getLogger(__name__)

class hr_attendance(models.Model):
    _inherit = "hr.attendance"
    
    def _si_so_custom(self, employee_id,name,action):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.
        """
#         for att in self.browse(cr, uid, ids, context=context):
            # search and browse for first previous and first next records
        #if type(name)==datetime:
        name =  name.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        _logger.info('nombre: %s empleado', name)

        prev_atts = self.search([('employee_id', '=', employee_id), ('name', '<', name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name DESC')
        next_atts = self.search([('employee_id', '=', employee_id), ('name', '>', name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name ASC')

        # check for alternance, return False if at least one condition is not satisfied
        if prev_atts and prev_atts[0].action == action: # previous exists and is same action
            _logger.info('coondicion 1')
            return False
        if next_atts and next_atts[0].action == action: # next exists and is same action
            _logger.info('coondicion 2')
            return False
        if (not prev_atts) and (not next_atts) and action != 'sign_in': # first attendance must be sign_in
            _logger.info('coondicion 3')
            return False
        return True
    
    @api.model
    def create(self,vals):
        if isinstance(vals['name']):
            res = super(hr_attendance,self).create(vals)
        else:
            create_record = self._si_so_custom(vals['employee_id'],vals['che'],vals['action'])
            _logger.info('salio del crear %s', create_record)
            if create_record:
                if type(vals['name'])==datetime:
                    vals['name'] =  vals['name'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                res = super(hr_attendance,self).create(vals)
                _logger.info('crea registro')
            else:
                _logger.info('es de mi funcion')
                raise UserError(_('Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)'))
        return res


