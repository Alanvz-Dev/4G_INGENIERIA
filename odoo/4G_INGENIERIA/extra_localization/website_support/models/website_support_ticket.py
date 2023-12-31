# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools
from random import randint
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import SUPERUSER_ID
from dateutil import tz
import re

import logging
_logger = logging.getLogger(__name__)


class WebsiteSupportTicket(models.Model):

    _name = "website.support.ticket"
    _description = "Website Support Ticket"
    _order = "create_date desc"
    _rec_name = "subject"
    _inherit = ['mail.thread']
    _translate = True

    @api.model
    def _read_group_state(self, states, domain, order):
        """ Read group customization in order to display all the states in the
            kanban view, even if they are empty
        """

        staff_replied_state = self.env['ir.model.data'].get_object('website_support',
                                                                   'website_ticket_state_staff_replied')
        customer_replied_state = self.env['ir.model.data'].get_object('website_support',
                                                                      'website_ticket_state_customer_replied')
        customer_closed = self.env['ir.model.data'].get_object('website_support',
                                                               'website_ticket_state_customer_closed')
        staff_closed = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_closed')

        exclude_states = [staff_replied_state.id, customer_replied_state.id, customer_closed.id, staff_closed.id]

        # state_ids = states._search([('id','not in',exclude_states)], order=order, access_rights_uid=SUPERUSER_ID)
        state_ids = states._search([], order=order, access_rights_uid=SUPERUSER_ID)

        return states.browse(state_ids)

    def _default_state(self):
        return self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')

    def _default_priority_id(self):
        default_priority = self.env['website.support.ticket.priority'].search([('sequence','=','1')])
        return default_priority[0]

    def _default_approval_id(self):
        try:
            return self.env['ir.model.data'].get_object('website_support', 'no_approval_required')
        except ValueError:
            return False

    channel = fields.Char(string="Channel", default="Manual")
    create_user_id = fields.Many2one('res.users', "Create User")
    priority_id = fields.Many2one('website.support.ticket.priority', default=_default_priority_id, string="Priority")
    parent_company_id = fields.Many2one(string="Parent Company", related="partner_id.company_id")
    partner_id = fields.Many2one('res.partner', string="Partner")
    partner_image = fields.Binary(related='partner_id.image_medium', string="Partner image", readonly='True')
    user_id = fields.Many2one('res.users', string="Assigned User")
    person_name = fields.Char(string='Name')
    email = fields.Char(string="Email")
    support_email = fields.Char(string="Support Email")
    category = fields.Many2one('website.support.ticket.categories', string="Category", track_visibility='onchange')
    sub_category_id = fields.Many2one('website.support.ticket.subcategory', string="Sub Category")
    subject = fields.Char(string="Subject")
    description = fields.Text(string="Description")
    state = fields.Many2one('website.support.ticket.states', group_expand='_read_group_state', default=_default_state,
                            string="State")
    state_id = fields.Integer(related='state.id', string="State ID")
    conversation_history = fields.One2many('website.support.ticket.message', 'ticket_id', string="Conversation History")
    attachment = fields.Binary(string="Attachments")
    attachment_filename = fields.Char(string="Attachment Filename")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'website.support.ticket')],
                                     string="Media Attachments")
    unattended = fields.Boolean(string="Unattended", compute="_compute_unattend", store="True",
                                help="In 'Open' state or 'Customer Replied' state taken into consideration name changes")
    portal_access_key = fields.Char(string="Portal Access Key")
    ticket_number = fields.Char(string="Ticket Number", readonly=True)
    ticket_color = fields.Char(related="priority_id.color", string="Ticket Color")
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('website.support.ticket') )
    support_rating = fields.Integer(string="Support Rating")
    support_comment = fields.Text(string="Support Comment")
    close_comment = fields.Text(string="Close Comment")
    close_time = fields.Datetime(string="Close Time")
    close_date = fields.Date(string="Close Date")
    closed_by_id = fields.Many2one('res.users', string="Closed By")
    close_lock = fields.Boolean(string="Close Lock")
    time_to_close = fields.Integer(string="Time to close (seconds)")
    extra_field_ids = fields.One2many('website.support.ticket.field', 'wst_id', string="Extra Details")
    planned_time = fields.Datetime(string="Planned Time")
    planned_time_format = fields.Char(string="Planned Time Format", compute="_compute_planned_time_format")
    approval_id = fields.Many2one('website.support.ticket.approval', default=_default_approval_id, string="Approval")
    approval_message = fields.Text(string="Approval Message")
    approve_url = fields.Char(compute="_compute_approve_url", string="Approve URL")
    disapprove_url = fields.Char(compute="_compute_disapprove_url", string="Disapprove URL")
    tag_ids = fields.Many2many('website.support.ticket.tag', string="Tags")
    sla_id = fields.Many2one('website.support.sla', string="SLA")
    sla_timer = fields.Float(string="SLA Time Remaining")
    sla_timer_format = fields.Char(string="SLA Timer Format", compute="_compute_sla_timer_format")
    sla_active = fields.Boolean(string="SLA Active")
    sla_response_category_id = fields.Many2one('website.support.sla.response', string="(DEPRICATED) SLA Response Category")
    sla_rule_id = fields.Many2one('website.support.sla.rule', string="SLA Rule")
    sla_alert_ids = fields.Many2many('website.support.sla.alert', string="SLA Alerts",
                                     help="Keep record of SLA alerts sent so we do not resend them")

    @api.multi
    @api.depends('subject', 'ticket_number')
    def name_get(self):
        res = []
        for record in self:
            if record.subject and record.ticket_number:
                name = record.subject + " (#" + record.ticket_number + ")"
            else:
                name = record.subject
            res.append((record.id, name))
        return res
        
    @api.one
    @api.depends('sla_timer')
    def _compute_sla_timer_format(self):
        # Display negative hours in a positive format
        self.sla_timer_format = '{0:02.0f}:{1:02.0f}'.format(*divmod(abs(self.sla_timer) * 60, 60))

    @api.model
    def update_sla_timer(self):

        # Subtract 1 minute from the timer of all active SLA tickets, this includes going into negative
        for active_sla_ticket in self.env['website.support.ticket'].search([
            ('sla_active','=',True),
            ('sla_id','!=',False),
            '|',
            ('sla_response_category_id','!=',False),
            ('sla_rule_id','!=',False)
        ]):

            # If we only countdown during busines hours
            if active_sla_ticket.sla_rule_id.countdown_condition == 'business_only':
                # Check if the current time aligns with a timeslot in the settings,
                # setting has to be set for business_only or UserError occurs
                setting_business_hours_id = self.env['ir.default'].get('website.support.settings', 'business_hours_id')
                current_hour = datetime.datetime.now().hour
                current_minute = datetime.datetime.now().minute / 60
                current_hour_float = current_hour + current_minute
                day_of_week = datetime.datetime.now().weekday()
                during_work_hours = self.env['resource.calendar.attendance'].search([('calendar_id','=', setting_business_hours_id), ('dayofweek','=',day_of_week), ('hour_from','<',current_hour_float), ('hour_to','>',current_hour_float)])

                # If holiday module is installed take into consideration
                holiday_module = self.env['ir.module.module'].search([('name','=','hr_public_holidays'), ('state','=','installed')])
                if holiday_module:
                    holiday_today = self.env['hr.holidays.public.line'].search([('date','=',datetime.datetime.now().date())])
                    if holiday_today:
                        during_work_hours = False

                if during_work_hours:
                    active_sla_ticket.sla_timer -= 1/60
            elif active_sla_ticket.sla_rule_id.countdown_condition == '24_hour':
                #Countdown even if the business hours setting is not set
                active_sla_ticket.sla_timer -= 1/60
                
            #(DEPRICATED use sla_rule_id) If we only countdown during busines hours
            if active_sla_ticket.sla_response_category_id.countdown_condition == 'business_only':
                # Check if the current time aligns with a timeslot in the settings,
                # setting has to be set for business_only or UserError occurs
                setting_business_hours_id = self.env['ir.default'].get('website.support.settings', 'business_hours_id')
                current_hour = datetime.datetime.now().hour
                current_minute = datetime.datetime.now().minute / 60
                current_hour_float = current_hour + current_minute
                day_of_week = datetime.datetime.now().weekday()
                during_work_hours = self.env['resource.calendar.attendance'].search([('calendar_id','=', setting_business_hours_id), ('dayofweek','=',day_of_week), ('hour_from','<',current_hour_float), ('hour_to','>',current_hour_float)])

                # If holiday module is installed take into consideration
                holiday_module = self.env['ir.module.module'].search([('name','=','hr_public_holidays'), ('state','=','installed')])
                if holiday_module:
                    holiday_today = self.env['hr.holidays.public.line'].search([('date','=',datetime.datetime.now().date())])
                    if holiday_today:
                        during_work_hours = False

                if during_work_hours:
                    active_sla_ticket.sla_timer -= 1/60
            elif active_sla_ticket.sla_response_category_id.countdown_condition == '24_hour':
                #Countdown even if the business hours setting is not set
                active_sla_ticket.sla_timer -= 1/60

            #Send an email out to everyone in the category about the SLA alert
            notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_sla_alert')

            for sla_alert in self.env['website.support.sla.alert'].search([('vsa_id','=',active_sla_ticket.sla_id.id), ('alert_time','>=', active_sla_ticket.sla_timer)]):

                #Only send out the alert once
                if sla_alert not in active_sla_ticket.sla_alert_ids:

                    for my_user in active_sla_ticket.category.cat_user_ids:
                        values = notification_template.generate_email(active_sla_ticket.id)
                        values['body_html'] = values['body_html'].replace("_user_name_",  my_user.partner_id.name)
                        values['email_to'] = my_user.partner_id.email

                        send_mail = self.env['mail.mail'].create(values)
                        send_mail.send()

                        #Remove the message from the chatter since this would bloat the communication history by a lot
                        send_mail.mail_message_id.res_id = 0

                    #Add the alert to the list of already sent SLA
                    active_sla_ticket.sla_alert_ids = [(4, sla_alert.id)]

    def pause_sla(self):
        self.sla_active = False

    def resume_sla(self):
        self.sla_active = True

    @api.one
    @api.depends('planned_time')
    def _compute_planned_time_format(self):

        #If it is assigned to the partner, use the partners timezone and date formatting
        if self.planned_time and self.partner_id and self.partner_id.lang:
            partner_language = self.env['res.lang'].search([('code','=', self.partner_id.lang)])[0]

            my_planned_time = datetime.datetime.strptime(self.planned_time, DEFAULT_SERVER_DATETIME_FORMAT)

            #If we have timezone information translate the planned date to local time otherwise UTC
            if self.partner_id.tz:
                my_planned_time = my_planned_time.replace(tzinfo=tz.gettz('UTC'))
                local_time = my_planned_time.astimezone(tz.gettz(self.partner_id.tz))
                self.planned_time_format = local_time.strftime(partner_language.date_format + " " + partner_language.time_format) + " " + self.partner_id.tz
            else:
                self.planned_time_format = my_planned_time.strftime(partner_language.date_format + " " + partner_language.time_format) + " UTC"

        else:
            self.planned_time_format = self.planned_time

    @api.one
    def _compute_approve_url(self):
        self.approve_url = "/support/approve/" + str(self.id)

    @api.one
    def _compute_disapprove_url(self):
        self.disapprove_url = "/support/disapprove/" + str(self.id)

    @api.onchange('category')
    def _onchange_category(self):
        self.sub_category_id = False

    @api.onchange('sub_category_id')
    def _onchange_sub_category_id(self):
        if self.sub_category_id:

            add_extra_fields = []

            for extra_field in self.sub_category_id.additional_field_ids:
                add_extra_fields.append((0, 0, {'name': extra_field.name}))

            self.update({
                'extra_field_ids': add_extra_fields,
            })

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.person_name = self.partner_id.name
        self.email = self.partner_id.email

    def message_new(self, msg, custom_values=None):
        """ Create new support ticket upon receiving new email"""

        defaults = {'support_email': msg.get('to'), 'subject': msg.get('subject')}

        #Extract the name from the from email if you can
        if "<" in msg.get('from') and ">" in msg.get('from'):
            start = msg.get('from').rindex( "<" ) + 1
            end = msg.get('from').rindex( ">", start )
            from_email = msg.get('from')[start:end]
            from_name = msg.get('from').split("<")[0].strip()
            defaults['person_name'] = from_name
        else:
            from_email = msg.get('from')

        defaults['email'] = from_email
        defaults['channel'] = "Email"

        #Try to find the partner using the from email
        search_partner = self.env['res.partner'].sudo().search([('email','=', from_email)])
        if len(search_partner) > 0:
            defaults['partner_id'] = search_partner[0].id
            defaults['person_name'] = search_partner[0].name

        defaults['description'] = tools.html_sanitize(msg.get('body'))

        #Assign to default category
        setting_email_default_category_id = self.env['ir.default'].get('website.support.settings', 'email_default_category_id')

        if setting_email_default_category_id:
            defaults['category'] = setting_email_default_category_id

        return super(WebsiteSupportTicket, self).message_new(msg, custom_values=defaults)

    def message_update(self, msg_dict, update_vals=None):
        """ Override to update the support ticket according to the email. """

        if self.close_lock:
            # Send lock email
            setting_ticket_lock_email_template_id = self.env['ir.default'].get('website.support.settings', 'ticket_lock_email_template_id')
            if setting_ticket_lock_email_template_id:
                mail_template = self.env['mail.template'].browse(setting_ticket_lock_email_template_id)
            else:
                # BACK COMPATABLITY FAIL SAFE
                mail_template = self.env['ir.model'].get_object('website_support', 'support_ticket_close_lock')

            mail_template.send_mail(self.id, True)
            
            return False

        body_short = tools.html_sanitize(msg_dict['body'])
        #body_short = tools.html_email_clean(msg_dict['body'], shorten=True, remove=True)

        #Add to message history to keep HTML clean
        self.conversation_history.create({'ticket_id': self.id, 'by': 'customer', 'content': body_short })

        #If the to email address is to the customer then it must be a staff member
        if msg_dict.get('to') == self.email:
            change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')
        else:
            change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_customer_replied')

        self.state = change_state.id

        return super(WebsiteSupportTicket, self).message_update(msg_dict, update_vals=update_vals)

    @api.one
    @api.depends('state')
    def _compute_unattend(self):
        #BACK COMPATABLITY Use open and customer reply as default unattended states
        opened_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        customer_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')

        if self.state == opened_state or self.state == customer_replied_state or self.state.unattended == True:
            self.unattended = True

    @api.multi
    def request_approval(self):

        approval_email = self.env['ir.model.data'].get_object('website_support', 'support_ticket_approval')

        values = self.env['mail.compose.message'].generate_email_for_composer(approval_email.id, [self.id])[self.id]

        request_message = values['body']

        return {
            'name': "Request Approval",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.compose',
            'context': {'default_ticket_id': self.id, 'default_email': self.email, 'default_subject': self.subject, 'default_approval': True, 'default_body': request_message},
            'target': 'new'
        }

    @api.multi
    def open_reply_ticket_wizard(self):

        context = {'default_ticket_id': self.id, 'default_partner_id': self.partner_id.id, 'default_email': self.email, 'default_subject': self.subject}

        if self.partner_id.ticket_default_email_cc:
            context['default_email_cc'] = self.partner_id.ticket_default_email_cc
        if self.partner_id.ticket_default_email_body:
            context['default_body'] = self.partner_id.ticket_default_email_body

        return {
            'name': "Support Ticket Compose",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.compose',
            'context': context,
            'target': 'new'
        }

    @api.multi
    def open_close_ticket_wizard(self):

        return {
            'name': "Close Support Ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.close',
            'context': {'default_ticket_id': self.id},
            'target': 'new'
        }

    @api.multi
    def merge_ticket(self):
        return {
            'name': "Merge Support Ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.merge',
            'context': {'default_ticket_id': self.id},
            'target': 'new'
        }

    @api.model
    def _needaction_domain_get(self):
        open_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        custom_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')
        return ['|',('state', '=', open_state.id ), ('state', '=', custom_replied_state.id)]

    @api.model
    def create(self, vals):
        # Get next ticket number from the sequence
        vals['ticket_number'] = self.env['ir.sequence'].next_by_code('website.support.ticket')

        new_id = super(WebsiteSupportTicket, self).create(vals)

        new_id.portal_access_key = randint(1000000000,2000000000)

        ticket_open_email_template = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open').mail_template_id
        ticket_open_email_template.send_mail(new_id.id, True)

        setting_auto_create_contact = self.env['ir.default'].get('website.support.settings', 'auto_create_contact')
        if setting_auto_create_contact and new_id.person_name and new_id.email and not new_id.partner_id:
            new_partner = self.env['res.partner'].sudo().create({'name': new_id.person_name, 'email': new_id.email})
            new_id.partner_id = new_partner.id

        #If the customer has a dedicated support user then automatically assign them
        if new_id.partner_id.dedicated_support_user_id:
            new_id.user_id = new_id.partner_id.dedicated_support_user_id.id

        #Check if this contact has a SLA assigned
        if new_id.partner_id.sla_id:
            
            #Go through all rules starting from the lowest response time
            for sla_rule in new_id.partner_id.sla_id.rule_ids:
                #All conditions have to match
                all_true = True
                for sla_rule_con in sla_rule.condition_ids:
                    if sla_rule_con.type == "category" and new_id.category.id != sla_rule_con.category_id.id:
                        all_true = False
                    elif sla_rule_con.type == "subcategory" and new_id.sub_category_id.id != sla_rule_con.subcategory_id.id:
                        all_true = False
                    elif sla_rule_con.type == "priority" and new_id.priority_id.id != sla_rule_con.priority_id.id:
                        all_true = False
                
                if all_true:
                    new_id.sla_id = new_id.partner_id.sla_id.id
                    new_id.sla_active = True
                    new_id.sla_timer = sla_rule.response_time
                    new_id.sla_rule_id = sla_rule.id
                    break

            #(DEPRICATED) Check if this category has a SLA response time
            category_response = self.env['website.support.sla.response'].search([('vsa_id','=',new_id.partner_id.sla_id.id), ('category_id','=',new_id.category.id)])
            if category_response:
                new_id.sla_id = new_id.partner_id.sla_id.id
                new_id.sla_active = True
                new_id.sla_timer = category_response.response_time
                new_id.sla_response_category_id = category_response.id

        #Send an email out to everyone in the category
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category')
        support_ticket_menu = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_menu')
        support_ticket_action = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_action')

        #Add them as a follower to the ticket so they are aware of any internal notes
        new_id.message_subscribe_users(user_ids=new_id.category.cat_user_ids.ids)

        for my_user in new_id.category.cat_user_ids:
            values = notification_template.generate_email(new_id.id)
            values['body_html'] = values['body_html'].replace("_ticket_url_", "web#id=" + str(new_id.id) + "&view_type=form&model=website.support.ticket&menu_id=" + str(support_ticket_menu.id) + "&action=" + str(support_ticket_action.id) ).replace("_user_name_",  my_user.partner_id.name)
            values['email_to'] = my_user.partner_id.email

            send_mail = self.env['mail.mail'].create(values)
            send_mail.send()

            #Remove the message from the chatter since this would bloat the communication history by a lot
            send_mail.mail_message_id.res_id = 0

        return new_id

    @api.multi
    def write(self, values, context=None):

        update_rec = super(WebsiteSupportTicket, self).write(values)

        if 'state' in values:
            if self.state.mail_template_id:
                self.state.mail_template_id.send_mail(self.id, True)

        #Email user if category has changed
        if 'category' in values:
            change_category_email = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category_change')
            change_category_email.send_mail(self.id, True)

        if 'user_id' in values:
            setting_change_user_email_template_id = self.env['ir.default'].get('website.support.settings', 'change_user_email_template_id')

            if setting_change_user_email_template_id:
                email_template = self.env['mail.template'].browse(setting_change_user_email_template_id)
            else:
                #Default email template
                email_template = self.env['ir.model.data'].get_object('website_support','support_ticket_user_change')

            email_values = email_template.generate_email([self.id])[self.id]
            email_values['model'] = "website.support.ticket"
            email_values['res_id'] = self.id
            assigned_user = self.env['res.users'].browse( int(values['user_id']) )
            email_values['email_to'] = assigned_user.partner_id.email
            email_values['body_html'] = email_values['body_html'].replace("_user_name_", assigned_user.name)
            email_values['body'] = email_values['body'].replace("_user_name_", assigned_user.name)
            email_values['reply_to'] = email_values['reply_to']
            send_mail = self.env['mail.mail'].create(email_values)
            send_mail.send()


        return update_rec

    def send_survey(self):
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_survey')
        values = notification_template.generate_email(self.id)
        send_mail = self.env['mail.mail'].create(values)
        send_mail.send(True)

    # by Cooby tec
    @api.multi
    def toggle_reopen_ticket(self):
        self.close_time = False

        # Also reset the date for gamification
        self.close_date = False
        open_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        self.state = open_state.id

    @api.multi
    def toggle_shift_priority(self):
        priority_obj = self.env['website.support.ticket.priority']
        for ticket in self:
            if ticket.priority_id and ticket.priority_id.sequence:
                next_priority = priority_obj.search([('sequence', '>', ticket.priority_id.sequence)], order='sequence',
                                                    limit=1)
                if next_priority:  # if there's next priority, assign it that one
                    ticket.priority_id = next_priority.id
                else:
                    first_priority = priority_obj.search([], order='sequence', limit=1)
                    if first_priority:  # if there isn't, assign the lowest priority (since the button is a toggle)
                        ticket.priority_id = first_priority.id

    @api.multi
    def action_assign_me(self):
        # Assign current user
        self.user_id = self._uid

class WebsiteSupportTicketApproval(models.Model):

    _name = "website.support.ticket.approval"

    wst_id = fields.Many2one('website.support.ticket', string="Support Ticket")
    name = fields.Char(string="Name", translate=True)

class WebsiteSupportTicketMerge(models.TransientModel):

    _name = "website.support.ticket.merge"

    ticket_id = fields.Many2one('website.support.ticket', ondelete="cascade", string="Support Ticket")
    merge_ticket_id = fields.Many2one('website.support.ticket', ondelete="cascade", required="True", string="Merge With")

    @api.multi
    def merge_tickets(self):

        self.ticket_id.close_time = datetime.datetime.now()

        #Also set the date for gamification
        self.ticket_id.close_date = datetime.date.today()

        diff_time = datetime.datetime.strptime(self.ticket_id.close_time, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(self.ticket_id.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        self.ticket_id.time_to_close = diff_time.seconds

        closed_state = self.env['ir.model.data'].sudo().get_object('website_support', 'website_ticket_state_staff_closed')
        self.ticket_id.state = closed_state.id

        # Lock the ticket to prevent reopening
        self.ticket_id.close_lock = True
        
        # Send merge email
        setting_ticket_merge_email_template_id = self.env['ir.default'].get('website.support.settings', 'ticket_merge_email_template_id')
        if setting_ticket_merge_email_template_id:
            mail_template = self.env['mail.template'].browse(setting_ticket_merge_email_template_id)
        else:
            # BACK COMPATABLITY FAIL SAFE
            mail_template = self.env['ir.model'].get_object('website_support', 'support_ticket_merge')

        mail_template.send_mail(self.id, True)

        # Add as follower to new ticket
        if self.ticket_id.partner_id:
            self.merge_ticket_id.message_subscribe([self.ticket_id.partner_id.id])

        return {
            'name': "Support Ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket',
            'res_id': self.merge_ticket_id.id
        }

class WebsiteSupportTicketField(models.Model):

    _name = "website.support.ticket.field"

    wst_id = fields.Many2one('website.support.ticket', string="Support Ticket")
    name = fields.Char(string="Label")
    value = fields.Char(string="Value")

class WebsiteSupportTicketMessage(models.Model):

    _name = "website.support.ticket.message"

    ticket_id = fields.Many2one('website.support.ticket', string='Ticket ID')
    by = fields.Selection([('staff','Staff'), ('customer','Customer')], string="By")
    content = fields.Html(string="Content")

class WebsiteSupportTicketCategories(models.Model):

    _name = "website.support.ticket.categories"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Category Name')
    cat_user_ids = fields.Many2many('res.users', string="Category Users")
    access_group_ids = fields.Many2many('res.groups', string="Access Groups", help="Restrict which users can select the category on the website form, none = everyone")

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.categories')
        values['sequence']=sequence
        return super(WebsiteSupportTicketCategories, self).create(values)

class WebsiteSupportTicketSubCategories(models.Model):

    _name = "website.support.ticket.subcategory"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Sub Category Name')
    parent_category_id = fields.Many2one('website.support.ticket.categories', required=True, string="Parent Category")
    additional_field_ids = fields.One2many('website.support.ticket.subcategory.field', 'wsts_id', string="Additional Fields")

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.subcategory')
        values['sequence']=sequence
        return super(WebsiteSupportTicketSubCategories, self).create(values)

class WebsiteSupportTicketSubCategoryField(models.Model):

    _name = "website.support.ticket.subcategory.field"

    wsts_id = fields.Many2one('website.support.ticket.subcategory', string="Sub Category")
    name = fields.Char(string="Label", required="True")
    type = fields.Selection([('textbox','Textbox'), ('many2one','Dropdown(m2o)')], default="textbox", required="True", string="Type")
    model_id = fields.Many2one('ir.model', string="Model")
    model_name = fields.Char(related="model_id.model", string="Model Name")
    filter = fields.Char(string="Filter", default="[]", required="True")

class WebsiteSupportTicketStates(models.Model):

    _name = "website.support.ticket.states"

    name = fields.Char(required=True, translate=True, string='State Name')
    mail_template_id = fields.Many2one('mail.template', domain="[('model_id','=','website.support.ticket')]", string="Mail Template", help="The mail message that the customer gets when the state changes")
    unattended = fields.Boolean(string="Unattended", help="If ticked, tickets in this state will appear by default")

class WebsiteSupportTicketPriority(models.Model):

    _name = "website.support.ticket.priority"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string="Priority Name")
    color = fields.Char(string="Color")

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.priority')
        values['sequence']=sequence
        return super(WebsiteSupportTicketPriority, self).create(values)

class WebsiteSupportTicketTag(models.Model):

    _name = "website.support.ticket.tag"

    name = fields.Char(required=True, translate=True, string="Tag Name")

class WebsiteSupportTicketUsers(models.Model):

    _inherit = "res.users"

    cat_user_ids = fields.Many2many('website.support.ticket.categories', string="Category Users")

class WebsiteSupportTicketClose(models.TransientModel):

    _name = "website.support.ticket.close"

    ticket_id = fields.Many2one('website.support.ticket', string="Ticket ID")
    message = fields.Html(string="Close Message")
    template_id = fields.Many2one('mail.template', string="Mail Template", domain="[('model_id','=','website.support.ticket'), ('built_in','=',False)]")
    attachment_ids = fields.Many2many('ir.attachment', 'sms_close_attachment_rel', 'sms_close_id', 'attachment_id', 'Attachments')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            values = self.env['mail.compose.message'].generate_email_for_composer(self.template_id.id, [self.ticket_id.id])[self.ticket_id.id]
            self.message = values['body']

    def close_ticket(self):

        self.ticket_id.close_time = datetime.datetime.now()

        #Also set the date for gamification
        self.ticket_id.close_date = datetime.date.today()

        diff_time = datetime.datetime.strptime(self.ticket_id.close_time, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(self.ticket_id.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        self.ticket_id.time_to_close = diff_time.seconds

        closed_state = self.env['ir.model.data'].sudo().get_object('website_support', 'website_ticket_state_staff_closed')

        #We record state change manually since it would spam the chatter if every 'Staff Replied' and 'Customer Replied' gets recorded
        message = "<ul class=\"o_mail_thread_message_tracking\">\n<li>State:<span> " + self.ticket_id.state.name + " </span><b>-></b> " + closed_state.name + " </span></li></ul>"
        self.ticket_id.message_post(body=message, subject="Ticket Closed by Staff")

        email_wrapper = self.env['ir.model.data'].get_object('website_support', 'support_ticket_close_wrapper')

        values = email_wrapper.generate_email([self.id])[self.id]
        values['model'] = "website.support.ticket"
        values['res_id'] = self.ticket_id.id

        for attachment in self.attachment_ids:
            values['attachment_ids'].append((4, attachment.id))

        send_mail = self.env['mail.mail'].create(values)
        send_mail.send()

        self.ticket_id.close_comment = self.message
        self.ticket_id.closed_by_id = self.env.user.id
        self.ticket_id.state = closed_state.id

        self.ticket_id.sla_active = False

        #Auto send out survey
        setting_auto_send_survey = self.env['ir.default'].get('website.support.settings', 'auto_send_survey')
        if setting_auto_send_survey:
            self.ticket_id.send_survey()

class WebsiteSupportTicketCompose(models.Model):

    _name = "website.support.ticket.compose"

    ticket_id = fields.Many2one('website.support.ticket', string='Ticket ID')
    partner_id = fields.Many2one('res.partner', string="Partner", readonly="True")
    email = fields.Char(string="Email", readonly="True")
    email_cc = fields.Char(string="Cc")
    subject = fields.Char(string="Subject", readonly="True")
    body = fields.Text(string="Message Body")
    template_id = fields.Many2one('mail.template', string="Mail Template", domain="[('model_id','=','website.support.ticket'), ('built_in','=',False)]")
    approval = fields.Boolean(string="Approval")
    planned_time = fields.Datetime(string="Planned Time")
    attachment_ids = fields.Many2many('ir.attachment', 'sms_compose_attachment_rel', 'sms_compose_id', 'attachment_id', 'Attachments')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            values = self.env['mail.compose.message'].generate_email_for_composer(self.template_id.id, [self.ticket_id.id])[self.ticket_id.id]
            self.body = values['body']

    @api.one
    def send_reply(self):

        #Change the approval state before we send the mail
        if self.approval:
            #Change the ticket state to awaiting approval
            awaiting_approval_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_awaiting_approval')
            self.ticket_id.state = awaiting_approval_state.id

            #One support request per ticket...
            self.ticket_id.planned_time = self.planned_time
            self.ticket_id.approval_message = self.body
            self.ticket_id.sla_active = False

        #Send email
        values = {}

        setting_staff_reply_email_template_id = self.env['ir.default'].get('website.support.settings', 'staff_reply_email_template_id')

        if setting_staff_reply_email_template_id:
            email_wrapper = self.env['mail.template'].browse(setting_staff_reply_email_template_id)

        values = email_wrapper.generate_email([self.id])[self.id]
        values['model'] = "website.support.ticket"
        values['res_id'] = self.ticket_id.id
        values['reply_to'] = email_wrapper.reply_to
        
        if self.email_cc:
            values['email_cc'] = self.email_cc

        for attachment in self.attachment_ids:
            values['attachment_ids'].append((4, attachment.id))

        send_mail = self.env['mail.mail'].create(values)
        send_mail.send()

        #Add to the message history to keep the data clean from the rest HTML
        self.env['website.support.ticket.message'].create({'ticket_id': self.ticket_id.id, 'by': 'staff', 'content':self.body.replace("<p>","").replace("</p>","")})

        #Post in message history
        #self.ticket_id.message_post(body=self.body, subject=self.subject, message_type='comment', subtype='mt_comment')

        if self.approval:
            #Also change the approval
            awaiting_approval = self.env['ir.model.data'].get_object('website_support','awaiting_approval')
            self.ticket_id.approval_id = awaiting_approval.id
        else:
            #Change the ticket state to staff replied
            staff_replied = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')
            self.ticket_id.state = staff_replied.id
