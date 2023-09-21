from odoo import models, fields, api

class balance_de_dias_laborados(models.Model):
    _name = 'hr_payroll_4g.balance_de_tiempo'
    departamento = fields.Many2one('hr.department')
    operador = fields.Many2one('hr.employee')
    active = fields.Boolean(default=True)
    #Estos campos serán computados en base a la tabla de historial de dias laborados

    horas_a_favor = fields.Float()
    horas_en_contra = fields.Float()
    aux_dias_a_favor = fields.Float(compute='get_total_de_horas_a_favor')
    aux_dias_en_contra = fields.Float(compute='get_total_de_horas_en_contra')
    
    
    
    @api.multi
    def get_total_de_horas_a_favor(self):
        for item in self:
            horas_a_favor=0
            historial_de_horas_objs=self.env['hr_payroll_4g.historial_de_tiempo'].search([('operador','in',[item.operador.id]),('state','in',['approve'])])
            for historial in historial_de_horas_objs:
                horas_a_favor=horas_a_favor+historial.horas_a_favor
            
            #Le carga los dias a cada empleado
            
            item.write({'horas_a_favor':horas_a_favor})
            print(item)
            print(item.horas_a_favor)
            
        print(item)

    @api.multi
    def get_total_de_horas_en_contra(self):
        for item in self:
            horas_en_contra=0
            historial_de_horas_objs=self.env['hr_payroll_4g.historial_de_tiempo'].search([('operador','in',[item.operador.id]),('state','in',['approve'])])
            for historial in historial_de_horas_objs:
                horas_en_contra=horas_en_contra+historial.horas_en_contra
            #Le carga los dias a cada empleado
            item.write({'horas_en_contra':horas_en_contra})
            print(item)
            print(item.horas_en_contra)
            print('c')
            
        



    #Boton para ver el historial con los filtros pendientes