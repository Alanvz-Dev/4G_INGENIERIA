#Preguntar fecha de inicio y fin
import pandas as pd

#Si la semana de pago de 2022 inicia el 27 de diciembre de 2021 desde que fecha se deben tomar las utilidades
res = []
count = 0
payslips = self.env['hr.payslip'].search([("state","=","done"),("estado_factura","=","factura_correcta"),("fecha_pago",">=","2022-01-01"),("fecha_pago","<=","2022-12-31")])
contracts = self.env['hr.contract'].search([('employee_id','!=',False)]).ids
total = len(contracts)
for contract_id in contracts:
    slips = payslips.filtered(lambda payslip: payslip.contract_id.id == contract_id).mapped('line_ids').filtered(lambda line_ids: line_ids.code == 'P001')
    res = res + [(slip.employee_id.id,slip.slip_id.payslip_run_id.name,slip.slip_id.name,slip.slip_id.estado_factura,slip.slip_id.folio_fiscal,slip.slip_id.employee_id.name,slip.code,slip.name, slip.amount) for slip in slips]
    count = count+1
    print('%s de %s'%(count,total))
    
df = pd.DataFrame([{'ID': tup[0],'Nómina': tup[1], 'Documento Origen': tup[2], 'Estado de Factura': tup[3], 'Folio Fiscal': tup[4], 'Colaborador': tup[5],'Codigo': tup[6],'Desc. Cod': tup[7],'Monto': tup[8]} for tup in res])
df.to_excel('datos4.xlsx', index=False)

   