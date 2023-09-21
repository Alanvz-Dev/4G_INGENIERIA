from odoo import _, api, fields, models
import io
import base64


class CreateAtachment(models.AbstractModel):
    _name = 'sua.create_attachtment'

    @api.multi
    def generate_sua_file(self):
        lines =[]
        for line in self:
            x = line.complete_row_afil
            if x:
                lines.append(x+'\r')
        # Write a string to a buffer
        output = io.StringIO()
        output.writelines(lines)
        print(type(output))
        # Retrieve the value written
        print(output.getvalue())
        print(type(output.getvalue().encode()))
        # Discard buffer memory


        # output is where you have the content of your file, it can be
        # any type of content
        output 
        # encode
        result = base64.b64encode(output.getvalue().encode("iso-8859-1"))
        output.close()
        # get base url
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        # create attachment
        attachment_id = attachment_obj.create(
        	{'name': "name", 'datas_fname': 'name.txt', 'datas': result})
        # prepare download url
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        # download
        return {
        	"type": "ir.actions.act_url",
        	"url": str(base_url) + str(download_url),
        	"target": "new",
        }    
