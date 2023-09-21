from collections import defaultdict
from datetime import date, datetime, timedelta
import pytz

from odoo import api, exceptions, fields, models, _

class mail_activity(models.AbstractModel):
    _inherit = 'mail.activity'

    def action_feedback(self, feedback=False):
        message = self.env['mail.message']
        if feedback:
            self.write(dict(feedback=feedback))

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for activity in self:
            record = self.env[activity.res_model].browse(activity.res_id)
            try:
                record.message_post_with_view(
                    'mail.message_activity_done',
                    values={'activity': activity},
                    subtype_id=self.env.ref('mail.mt_activities').id,
                    mail_activity_type_id=activity.activity_type_id.id,
                )                
            except Exception as e:
                print(e)


            # Moving the attachments in the message
            # TODO: Fix void res_id on attachment when you create an activity with an image
            # directly, see route /web_editor/attachment/add
            activity_message = record.message_ids[0]
            message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
            message_attachments.write({
                'res_id': activity_message.id,
                'res_model': activity_message._name,
            })
            activity_message.attachment_ids = message_attachments
            message |= activity_message

        self.unlink()
        return message.ids and message.ids[0] or False
