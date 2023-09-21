from odoo import _, api, fields, models

class agregar_monto(models.TransientModel):
    _name = 'flujo_efectivo.agregar_monto'
    _description = 'agregar_monto'
    
    partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto')
    bank_id = fields.Many2one(comodel_name='account.journal', string='Banco')
    date = fields.Date(string='Fecha', required=True)
    required_amount = fields.Integer(string="Monto requerido", required=True)
    descripcion = fields.Text(string='Nota')
    tipo_de_flujo = fields.Selection(
        string='Tipo de Monto',
        selection=[('ldc','Línea de Crédito'), ('sdb','Saldo de Banco')],
        required=True
    )
    tipo = fields.Selection(
        string='Tipo de Flujo',
        selection=[('in', 'Ingreso'), ('out', 'Egreso')],
        required=True
    ) 
    tipo_credito = fields.Selection([
        ('fact', 'Factoraje'),('lcs', 'Línea de Crédito Simple'),('lcr', 'Linea de Crédito Revolvente')
    ], string='Típo de Crédito')

    fecha_pago = fields.Date(string='Fecha de Pago')
    
    def agregar_monto(self):
        if self.tipo_de_flujo =='ldc':
            balance_bank_vals = {
            "date_line_credit":self.date,
            "name":self.bank_id.id,
            "required_amount": abs(self.required_amount),
            "descripcion":self.descripcion,
            "fecha_pago": self.fecha_pago ,
            'tipo_credito':self.tipo_credito,
            'name':self.partner_id.id,
            'sub_categoria': dict((self._fields['tipo_credito'].selection)).get(self.tipo_credito).upper()
            }
            flujo_efectivo_vals = {
            'monto': abs(self.required_amount),
            'tipo':'in',
            'fecha_programada':self.date,
            'categoria':'LINEA DE CREDITO',
            'entidad':self.partner_id.name,
            'fecha_pago': self.fecha_pago,
            'sub_categoria': dict((self._fields['tipo_credito'].selection)).get(self.tipo_credito).upper()
            }
            self.env['flujo_efectivo.credit_line'].create(balance_bank_vals)
            self.env['flujo_efectivo.flujo_efectivo'].create(flujo_efectivo_vals)

            flujo_efectivo_vals_fecha_pago = {
            'monto': -1*abs(self.required_amount),
            'tipo': 'out',
            'fecha_programada':self.date,
            'categoria':'PAGO LINEA DE CREDITO',
            'entidad':self.partner_id.name,
            'fecha_pago': self.fecha_pago,
            'sub_categoria': dict((self._fields['tipo_credito'].selection)).get(self.tipo_credito).upper()
            }

            self.env['flujo_efectivo.flujo_efectivo'].create(flujo_efectivo_vals_fecha_pago)
            
        if self.tipo_de_flujo =='sdb':
            balance_bank_vals = {
            "date_balance":self.date,
            "name":self.bank_id.id,
            "balance_today": abs(self.required_amount),
            "descripcion":self.descripcion,
            'sub_categoria':'SALDO DE BANCOS',
            }     
            flujo_efectivo_vals = {
            'monto': abs(self.required_amount),
            'tipo':self.tipo,
            'fecha_programada':self.date,
            'categoria':'BANCOS',
            'sub_categoria':'SALDO DE BANCOS',
            'entidad':self.bank_id.name
            }
            self.env['flujo_efectivo.balance_bank'].create(balance_bank_vals)
            self.env['flujo_efectivo.flujo_efectivo'].create(flujo_efectivo_vals)


        









    
