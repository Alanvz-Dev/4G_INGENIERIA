from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Dirección Carta Porte'

    @api.onchange('zip')
    def _onchange_zip(self):
        try:
            datos_colonia_completos= self.env['cfdi_traslado_ext.catalogo_colonia'].search([('c_codigoPostal','in',[self.zip])])
            #Estdo Localidad Municipio
            # datos_colonia=self.env['catalogos.colonias'].search([('c_codigopostal','in',[self.zip])])
            datos_localidades=self.env['catalogos.localidades'].search([('c_localidad','in',[datos_colonia_completos.c_localidad]),('c_estado','in',[datos_colonia_completos.c_estado])])
            # datos_localidades=self.env['catalogos.localidades'].search([('c_localidad','in',['07']),('c_estado','in',[datos_colonia_completos.c_estado])])
            datos_municipio=self.env['catalogos.municipio'].search([('c_municipio','in',[datos_colonia_completos.c_municipio]),('c_estado','in',[datos_colonia_completos.c_estado])])
            datos_estado=self.env['catalogos.estados'].search([('c_estado','in',[datos_colonia_completos.c_estado])])
            self.cce_clave_localidad=datos_localidades.id
            self.cce_clave_municipio=datos_municipio.id
            self.cce_clave_estado=datos_estado.id
        except:pass
    
