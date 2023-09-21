# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    porte_count = fields.Integer(compute='cfdi_porte_count')
    def create_cfdi_traslado_ext(self):
        contacto=self.env['cfdi_traslado_ext.config'].search([])
        if not contacto:
            raise ValidationError("Configure el valor por defecto para los campos Ubicaciones↳Remitente para el Origen y para Figura Transporte↳Propietarios↳Propietarios\nen el apartado CFDI Traslado Configuraciones")
        if len(contacto)>1:
            raise ValidationError("Solo puede existir una linea de configuraciones en CFDI Traslado Configuraciones, elimine y solo deje una")
            
        def get_wheight(product_id):
            try:
                return product_id.weight
            except:
                return 0
        lines = []
        for line in self.invoice_line_ids:
            lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'quantity': line.quantity,
                'price_unit': line.product_id.lst_price,
                'pesoenkg': get_wheight(line.product_id)
            }))
        ubicaciones_lines_origen = (0, 0, {
            'tipoubicacion': 'Origen',
            'contacto':contacto.contacto_propietario.id,
            'fecha':date.today()
        })

        ubicaciones_lines_destino = (0, 0, {
            'tipoubicacion': 'Destino',
            'contacto':self.partner_shipping_id.id,
            'fecha':date.today()
        })
        # The prefix default_ is mandatory for pass values to ahnother form
        context_cfdi_traslado = {
            'default_partner_id': self.partner_id.id,
            'default_invoice_date': self.date_invoice,
            'default_source_document': self.number,
            'default_uso_cfdi': self.uso_cfdi,
            'default_tipo_relacion': self.tipo_relacion,
            'default_uuid_relacionado': self.uuid_relacionado,
            'default_factura_line_ids': lines,
            'default_numerototalmercancias': sum(self.invoice_line_ids.mapped('quantity')),
            'default_ubicaciones_line_ids':[ubicaciones_lines_origen,ubicaciones_lines_destino],
            'default_propietarios_line_ids':[((0, 0, {'propietario_id':contacto.contacto_propietario.id}))],
            'default_cfdi_traslado_account_invoice':self.id
        }


        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cfdi.traslado',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'fullscreen',
            'context': context_cfdi_traslado
        }

    def get_cfdi_porte_recs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Carta Porte'+'→'+self.number,
            'view_mode': 'tree,form',
            'res_model': 'cfdi.traslado',
            'domain': [('cfdi_traslado_account_invoice', 'in', self.ids)],
            'context': {'cfdi_traslado_account_invoice': self.id,'create':False}
        }

    def cfdi_porte_count(self):
        self.porte_count = self.env['cfdi.traslado'].search_count([('cfdi_traslado_account_invoice', 'in', self.ids)])
