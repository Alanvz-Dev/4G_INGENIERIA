from odoo import _, api, fields, models


class EmployeeMovs(models.Model):
    _name = 'sua.states'

    #TODO Fix create and write values with uppercase
    estado_sua = fields.Selection([('NA', 'Sin Estatus'),('DRAFT', 'Por Cargar SUA'), ('DONE', 'Carga Correcta SUA')], string='Estado SUA',
    default='NA'
    )
    estado_idse = fields.Selection([('NA', 'Sin Estatus'),('DRAFT', 'Por Cargar IDSE'),('PROC', 'Espereando Respuesta IDSE'), ('DONE', 'Carga Correcta IDSE')], string='Estado IDSE',default='NA')

    def generar_registro_idse(self):
        pass


    

    
    

    
