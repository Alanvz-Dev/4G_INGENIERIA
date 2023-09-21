from odoo import _, api, fields, models
from odoo.modules.registry import Registry

class dining_service(models.Model):
    _description="Fecha y hora de Servicios"
    _name = 'dining_service.line'
    name = fields.Char()
    dining_service_detail = fields.Many2one('dining_service.detail', ondelete="cascade",copy=True)
    employee_contract_id = fields.Integer()
    date_time_service_line = fields.One2many('dinning_service.date_time', 'date_time_service', string='Servicios', ondelete="cascade",copy=True)    
    company = fields.Char()
    last_update = fields.Datetime(string='Último Registro')


    def discount_service(self):
        try:
            registry = Registry(self.company)
            cr = registry.cursor()
            env = api.Environment(cr, self.env.uid, {})
            contract = env['hr.contract'].sudo().browse(self.employee_contract_id)
            if contract:
                contract.dinning_service_count=contract.dinning_service_count+len(self.date_time_service_line)
                cr.commit()
                cr.close()
                env.reset()
                return contract
        except:
            pass

    def clear_services(self):
            databases = ['4G_INGENIERIA', 'FERREXTOOL']
            for database in databases:
                try:                    
                    registry = Registry(database)
                    cr = registry.cursor()
                    env = api.Environment(cr, self.env.uid, {})
                    contract = env['hr.contract'].sudo().search([])
                    for item in contract:
                        item.dinning_service_count=0

                    cr.commit()
                    cr.close()
                    env.reset()
                except:
                    pass