from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo.exceptions import UserError,ValidationError


class ResumenNomina(models.Model):
    _name = 'hr_payroll_pr.resumen_nomina'
    _description = 'Resumen Nómina'
    _rec_name = 'name'
    
    name = fields.Char(
        string='name',
    )
    
    hr_payslip_id = fields.Many2one('hr.payslip.run', string='Nómina')
    start_date = fields.Date(string='Del:')
    end_date = fields.Date(string='Al:')
    fecha_pago = fields.Date(string='Fecha de Pago')
    active = fields.Boolean(default=True)
    resumen_nomina_ids = fields.One2many('hr_payroll_pr.resumen_nomina_line', 'resumen_nomina_id',ondelete='cascade')
    no_nomina = fields.Selection(
        selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], string=_('Nómina del mes'))    
    record_name = fields.Char(compute='_compute_record_name', string='Nombre')
    
    
    def _compute_record_name(self):
        for record in self:
            record.name = 'Resumen Nomina'
    

    def recalcular(self):
        self.resumen_nomina_ids.get_total_de_horas()
        self.resumen_nomina_ids.compute_bonos()
        self.aplicar_bonos()

    def compute_bonos_1(self):
        for empleado in self.resumen_nomina_ids:
            empleado.compute_bonos_1()


    @api.multi
    def action_generar_resumen(self):
        hr_contract = self.env['hr.contract']
        employees = hr_contract.search([('employee_id', '!=', False), ('state', 'in', ['open'])]).mapped('employee_id')
        new_recs = []
        for employee in employees:
            new_recs.append((0, 0, {'operador': employee.id}))
        self.resumen_nomina_ids = new_recs

    @api.onchange('hr_payslip_id')
    def _get_fecha_final(self):
        if self.hr_payslip_id:
            self.start_date = datetime.strptime(
                self.hr_payslip_id.date_start, '%Y-%m-%d')
            self.end_date = datetime.strptime(
                self.hr_payslip_id.date_end, '%Y-%m-%d')
        else:
            self.start_date = ''
            self.end_date = ''



    @api.multi
    def action_open_payroll_create(self):

        payslip_run = self.env['hr.payslip.run'].with_context(resumen_nomina_id=self.id).create({
            "tipo_configuracion": 1,
    "tipo_nomina": "O",
    "periodicidad_pago": "02",
    "fecha_pago": self.fecha_pago,
    "date_start":  self.start_date,
    "date_end": self.end_date,
    "journal_id": 49,
    "name": self.name,
    "version_cfdi": "3",
    "estructura": False,
    'no_nomina':self.no_nomina
    
        })
        
        payslip_run._dias_pagar()
        payslip_run._get_frecuencia_pago()
        payslip_employee = self.env['hr.payslip.employees'].create({
            'employee_ids': [(6,0,self.resumen_nomina_ids.mapped('operador').ids)]
        })
        payslip_run._update_nominas_mes()
        payslip_run._get_imss_dias()
        payslip_run._compute_imss_mes()
        payslip_employee.with_context(resumen_nomina_id=self.id,active_id=payslip_run.id).compute_sheet()
   
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'view_mode': 'form',
            'res_model': 'hr.payslip.run',
            'target': 'main',
            'res_id': payslip_run.id,
        }

class ResumenNominaLine(models.Model):
    _name = 'hr_payroll_pr.resumen_nomina_line'
    _description = 'Resumen Nómina Line'
    resumen_nomina_id = fields.Many2one('hr_payroll_pr.resumen_nomina')
    operador = fields.Many2one('hr.employee')
    dia1 = fields.Many2one('hr_payroll_pr.mayordomia_line',compute='_compute_days', string='Día 1')
    dia2 = fields.Many2one('hr_payroll_pr.mayordomia_line',compute='_compute_days', string='Día 2')
    dia3 = fields.Many2one('hr_payroll_pr.mayordomia_line',compute='_compute_days', string='Día 3')
    dia4 = fields.Many2one('hr_payroll_pr.mayordomia_line',compute='_compute_days', string='Día 4')
    dia5 = fields.Many2one('hr_payroll_pr.mayordomia_line',compute='_compute_days', string='Día 5')
    dia6 = fields.Many2one('hr_payroll_pr.mayordomia_line',compute='_compute_days', string='Día 6')
    dia7 = fields.Many2one('hr_payroll_pr.mayordomia_line',compute='_compute_days', string='Día 7')
    bono_ids = fields.Many2many('hr_payroll_pr.bonos', compute='compute_bonos', string='Bonos')
    # incidencia_ids = fields.Many2many('hr_4g_payroll_ext.incidency')
    total_de_horas = fields.Float(compute='get_total_de_horas', string='Total de Horas a Pagar', digits=(12, 2), store=True)
    incidencia_ids = fields.Many2many(
        string='Incidencias',
        comodel_name='hr_4g_payroll_ext.incidency',
        relation='hr_4g_payroll_ext_incidency_resumen_nomina_line_rel',
        column1='incidency_id',
        column2='resumen_nomina_line_id',
        compute='_compute_incidencias'
    )
    
    def _compute_days(self):
        list_days = self.get_date_range_list()
        for record in self:
            count = 1
            for day in list_days:
                record.update({'dia%s' % (count): record.dia1.search(
                    [('mayordomia_id.fecha', 'in', [day]), ('operador', 'in', record.operador.ids)]).id})
                count = count+1
        return

    def get_date_range_list(self):
        for record in self:
            if record.resumen_nomina_id:
                days_list = []
                date_from_dt = datetime.strptime(
                    record.resumen_nomina_id.start_date, DEFAULT_SERVER_DATE_FORMAT)
                date_to_dt = datetime.strptime(
                    record.resumen_nomina_id.end_date, DEFAULT_SERVER_DATE_FORMAT)
                delta = date_to_dt - date_from_dt  # as timedelta
                days = [date_from_dt + timedelta(days=i)
                        for i in range(delta.days + 1)]
                for day in days:
                    days_list.append(datetime.strftime(
                        day, DEFAULT_SERVER_DATE_FORMAT))

                return days_list

    @api.depends('dia1', 'dia2', 'dia3', 'dia3', 'dia4', 'dia5', 'dia6', 'dia7')
    def get_total_de_horas(self):
        for item in self:
            item.total_de_horas = item.dia1.horas_a_pagar+item.dia2.horas_a_pagar+item.dia3.horas_a_pagar + \
                item.dia4.horas_a_pagar+item.dia5.horas_a_pagar + \
                item.dia6.horas_a_pagar+item.dia7.horas_a_pagar
            print(item.total_de_horas)

    @api.depends('dia1', 'dia2', 'dia3', 'dia3', 'dia4', 'dia5', 'dia6', 'dia7')
    def compute_bonos(self):
        for item in self:
            new_recs = []
            asistencia = item.dia1.search([('id', 'in', [item.dia1.id, item.dia2.id, item.dia3.id,
                                          item.dia4.id, item.dia5.id, item.dia6.id, item.dia7.id]), ('bonos_ids.codigo', 'in', ['A'])])
            puntualidad = item.dia1.search([('id', 'in', [item.dia1.id, item.dia2.id, item.dia3.id,
                                           item.dia4.id, item.dia5.id, item.dia6.id, item.dia7.id]), ('bonos_ids.codigo', 'in', ['P'])])
            if len(asistencia) == len(item.operador.turno.turno_line_ids):
                new_recs.append(item.bono_ids.search([('codigo', 'in', ['A'])]).id)
                item.operador.contract_id.bono_asistencia=True
            else:
                item.operador.contract_id.bono_asistencia=False

            if len(puntualidad) == len(item.operador.turno.turno_line_ids):
                new_recs.append(item.bono_ids.search([('codigo', 'in', ['P'])]).id)
                item.operador.contract_id.bono_puntualidad=True
            else:
                item.operador.contract_id.bono_puntualidad=False

            item.bono_ids = [(6, 0, new_recs)]

    def compute_bonos_1(self):
        for item in self:
            new_recs = []
            asistencia = item.dia1.search([('id', 'in', [item.dia1.id, item.dia2.id, item.dia3.id,
                                          item.dia4.id, item.dia5.id, item.dia6.id, item.dia7.id]), ('bonos_ids.codigo', 'in', ['A'])])
            puntualidad = item.dia1.search([('id', 'in', [item.dia1.id, item.dia2.id, item.dia3.id,
                                           item.dia4.id, item.dia5.id, item.dia6.id, item.dia7.id]), ('bonos_ids.codigo', 'in', ['P'])])
            if len(asistencia) == len(item.operador.turno.turno_line_ids):
                new_recs.append(item.bono_ids.search([('codigo', 'in', ['A'])]).id)
                item.operador.contract_id.bono_asistencia=True
            else:
                item.operador.contract_id.bono_asistencia=False

            if len(puntualidad) == len(item.operador.turno.turno_line_ids):
                new_recs.append(item.bono_ids.search([('codigo', 'in', ['P'])]).id)
                item.operador.contract_id.bono_puntualidad=True
            else:
                item.operador.contract_id.bono_puntualidad=False

            item.bono_ids = [(6, 0, new_recs)]

    @api.depends('dia1', 'dia2', 'dia3', 'dia3', 'dia4', 'dia5', 'dia6', 'dia7')
    def _compute_incidencias(self):
        for item in self:
            incidencia_ids = item.dia1.browse([item.dia1.id, item.dia2.id, item.dia3.id, item.dia4.id,
                                              item.dia5.id, item.dia6.id, item.dia7.id]).mapped('incidencia_ids').ids
            item.incidencia_ids = [(6, 0, incidencia_ids)]

    #    fields.many2many(
    # 'res.partner.category',
    # 'res_partner_category_rel',
    # 'partner_id',
    # 'category_id',
    # 'Categories')
