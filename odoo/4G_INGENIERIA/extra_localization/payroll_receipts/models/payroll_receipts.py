# -*- coding: utf-8 -*-

from odoo import models, fields, api
import os
import base64
class payroll_receipts(models.Model):
    _name = 'payroll_receipts.payroll_receipts'
    name_get='employee_id'
    name = fields.Char()
    name_payroll = fields.Char()
    
    
    xml = fields.Binary()
    document_fname_xml= fields.Char()
    pdf = fields.Binary()
    document_fname_pdf= fields.Char()

    employee_id=fields.Many2one('hr.contract')
    date_from=fields.Date()
    date_to=fields.Date()
    id_payroll=fields.Integer()
    
    search_ids = fields.Char(
        compute="_compute_search_ids", search='search_ids_search1')

    @api.model
    def _get_uid(self):
        return self._uid



    @api.one
    @api.depends('name')
    def _compute_search_ids(self):
        print('View My Department CLO ACL')


    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 "%s (%s)" % (record.name, record.date_from)
                ))
        print(result)        
        return result



    def search_ids_search1(self,operator,operand):
        current_user_employee_id=self.env['resource.resource'].search([('user_id','in',[self._uid])]).ids

        employee=self.env['hr.employee'].search([('resource_id','in',current_user_employee_id)]).ids
        print(employee)


        contract=self.env['hr.contract'].search([('employee_id','in',employee)]).ids
        ##Exepcion si tiene dos contratos

        actual_payroll_receipts = self.env['payroll_receipts.payroll_receipts'].search([('employee_id','in',contract)]).mapped('id_payroll')
        payroll_objs=self.env['hr.payslip'].search([('estado_factura','in',['factura_correcta']),('contract_id','in',contract),('id','not in',actual_payroll_receipts)])

        print(payroll_objs)


   

            
        if payroll_objs:
            for payroll in payroll_objs:
                vals={}
                vals.update({'name_payroll':payroll.payslip_run_id.name})
                vals.update({'id_payroll':payroll.id})
                vals.update({'name':payroll.name})
                vals.update({'date_from':payroll.date_from})
                vals.update({'date_to':payroll.date_to})
                vals.update({'employee_id':payroll.contract_id.id})
                attachments=self.env['ir.attachment'].search([('res_model','=','hr.payslip'),('res_id','=',payroll.id)])
                if attachments:
                    try:
                        u=attachments[0]
                        g=attachments[1]
                 
                        pathxml='/opt/odoo/.local/share/Odoo/filestore/'+self.pool.db_name+'/'+attachments[0].store_fname
                        pathpdf='/opt/odoo/.local/share/Odoo/filestore/'+self.pool.db_name+'/'+attachments[1].store_fname
                        xml_file = open(pathxml,'rb')
                        xml_file_data=xml_file.read()
                        xml_file.close()
                        pdf_file = open(pathpdf,'rb')
                        pdf_file_data=pdf_file.read()
                        pdf_file.close()
                        encode_xml=base64.b64encode(xml_file_data)
                        encode_pdf=base64.b64encode(pdf_file_data)
                        x=attachments[0]
                        print(x)
                        print(attachments[0].name)
                        print(attachments[1].name)
                        vals.update({'document_fname_xml':attachments[0].name})
                        vals.update({'document_fname_pdf':attachments[1].name})
                        vals.update({'xml':encode_xml or False})
                        vals.update({'pdf':encode_pdf or False})
                    except:
                        print('err')
                        continue                        
                self.create(vals)
        else:
            obj = self.env['payroll_receipts.payroll_receipts'].search([('employee_id','in',contract)]).ids 
            print(obj)       
            return [('id', 'in', obj)]
        obj = self.env['payroll_receipts.payroll_receipts'].search([('employee_id','in',[contract.employee_id.ids])]).ids 
        print(obj)       
        return [('id', 'in', obj)]


    @api.multi
    def update_group_permissions(self):
        
        open_contracts=self.env['hr.contract'].search([('state','in',['open'])]).mapped('employee_id').ids
        employee=self.env['hr.employee'].search([('id','in',open_contracts)]).mapped('resource_id').ids
        resource=self.env['resource.resource'].search([('id','in',employee)]).mapped('user_id').ids
        group_id = self.env.ref('payroll_receipts.group_payroll_receipts')
        print(group_id)
        group_id.users = [(4, user) for user in resource]
        print(group_id)
        message_id = self.env['message.wizard'].create({'message': "Actualización exitosa"})
        return {
            'name': 'Successfull',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            # pass the id
            'res_id': message_id.id,
            'target': 'new'
        }



class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Text('Message', required=True)

    @api.multi
    def action_ok(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}

        
