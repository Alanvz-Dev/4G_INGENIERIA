# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval


class ProjectTaskType(models.Model):
    _name = 'project.task.type'
    _description = 'Task Stage'
    _order = 'sequence, id'

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    project_ids = fields.Many2many('project.project', 'project_task_type_rel', 'type_id', 'project_id', string='Projects',
        default=_get_default_project_ids)
    legend_priority = fields.Char(
        string='Starred Explanation', translate=True,
        help='Explanation text to help users using the star on tasks or issues in this stage.')
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready for Next Stage'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'project.task')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    

  

    @api.constrains('sequence')
    def on_move_stage(self):
        raise UserError(_('No se puede realizar el cambio de etapa, usted no tiene permisos, consulte a su Administrador'))
        


class Project(models.Model):
    _name = "project.project"
    _description = "Project"
    _inherit = ['mail.alias.mixin', 'mail.thread', 'portal.mixin']
    _inherits = {'account.analytic.account': "analytic_account_id"}
    _order = "sequence, name, id"
    _period_number = 5

    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'project.task')

    def get_alias_values(self):
        values = super(Project, self).get_alias_values()
        values['alias_defaults'] = {'project_id': self.id}
        return values

    @api.multi
    def unlink(self):
        analytic_accounts_to_delete = self.env['account.analytic.account']
        for project in self:
            if project.tasks:
                raise UserError(_('You cannot delete a project containing tasks. You can either delete all the project\'s tasks and then delete the project or simply deactivate the project.'))
            if project.analytic_account_id and not project.analytic_account_id.line_ids:
                analytic_accounts_to_delete |= project.analytic_account_id
        res = super(Project, self).unlink()
        analytic_accounts_to_delete.unlink()
        return res

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count([
                '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids)
            ])

    def _compute_task_count(self):
        task_data = self.env['project.task'].read_group([('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.task_count = result.get(project.id, 0)

    def _compute_task_needaction_count(self):
        projects_data = self.env['project.task'].read_group([
            ('project_id', 'in', self.ids),
            ('message_needaction', '=', True)
        ], ['project_id'], ['project_id'])
        mapped_data = {project_data['project_id'][0]: int(project_data['project_id_count'])
                       for project_data in projects_data}
        for project in self:
            project.task_needaction_count = mapped_data.get(project.id, 0)

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [
            '|',
            '&', ('res_model', '=', 'project.project'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.model
    def activate_sample_project(self):
        """ Unarchives the sample project 'project.project_project_data' and
            reloads the project dashboard """
        # Unarchive sample project
        project = self.env.ref('project.project_project_data', False)
        if project:
            project.write({'active': True})

        cover_image = self.env.ref('project.msg_task_data_14_attach', False)
        cover_task = self.env.ref('project.project_task_data_14', False)
        if cover_image and cover_task:
            cover_task.write({'displayed_image_id': cover_image.id})

        # Change the help message on the action (no more activate project)
        action = self.env.ref('project.open_view_project_all', False)
        action_data = None
        if action:
            action.sudo().write({
                "help": _('''<p class="oe_view_nocontent_create">Click to create a new project.</p>''')
            })
            action_data = action.read()[0]
        # Reload the dashboard
        return action_data

    def _compute_is_favorite(self):
        for project in self:
            project.is_favorite = self.env.user in project.favorite_user_ids

    def _inverse_is_favorite(self):
        favorite_projects = not_fav_projects = self.env['project.project'].sudo()
        for project in self:
            if self.env.user in project.favorite_user_ids:
                favorite_projects |= project
            else:
                not_fav_projects |= project

        # Project User has no write access for project.
        not_fav_projects.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_projects.write({'favorite_user_ids': [(3, self.env.uid)]})

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]
    change_state_locked=fields.Boolean(default=False)
    plantilla = fields.Selection([ ('platillagenerales', 'ADMINISTACIÓN DE PROYECTOS GENERALES'),('platillafabricacion', 'ADMINISTRACIÓN DE PROYECTOS DE FABRICACIÓN'),('platillatareas', 'ADMINISTRACIÓN DE TAREAS')])
    plantilla2021=fields.Boolean(help="This check is True when a new project is creted, so the old projects doesn't affected the new rules of templates made in 2020")
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide the project without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Projects.")
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Contract/Analytic',
        help="Link this project to an analytic account if you need financial management on projects. "
             "It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.",
        ondelete="cascade", required=True, auto_join=True)
    favorite_user_ids = fields.Many2many(
        'res.users', 'project_favorite_user_rel', 'project_id', 'user_id',
        default=_get_default_favorite_user_ids,
        string='Members')
    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite', string='Show Project on dashboard',
        help="Whether this project should be displayed on the dashboard or not")
    label_tasks = fields.Char(string='Use Tasks as', default='Tasks', help="Gives label to tasks on project's kanban view.")
    tasks = fields.One2many('project.task', 'project_id', string="Task Activities")
    resource_calendar_id = fields.Many2one(
        'resource.calendar', string='Working Time',
        default=lambda self: self.env.user.company_id.resource_calendar_id.id,
        help="Timetable working hours to adjust the gantt diagram report")
    type_ids = fields.Many2many('project.task.type', 'project_task_type_rel', 'project_id', 'type_id', string='Tasks Stages')
    task_count = fields.Integer(compute='_compute_task_count', string="Tasks")
    task_needaction_count = fields.Integer(compute='_compute_task_needaction_count', string="Tasks")
    task_ids = fields.One2many('project.task', 'project_id', string='Tasks',
                               domain=['|', ('stage_id.fold', '=', False), ('stage_id', '=', False)])
    color = fields.Integer(string='Color Index')
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user, track_visibility="onchange")
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict", required=True,
        help="Internal email associated with this project. Incoming emails are automatically synchronized "
             "with Tasks (or optionally Issues if the Issue Tracker module is installed).")
    privacy_visibility = fields.Selection([
            ('followers', 'On invitation only'),
            ('employees', 'Visible by all employees'),
            ('portal', 'Visible by following customers'),
        ],
        string='Privacy', required=True,
        default='employees',
        help="Holds visibility of the tasks or issues that belong to the current project:\n"
                "- On invitation only: Employees may only see the followed project, tasks or issues\n"
                "- Visible by all employees: Employees may see all project, tasks or issues\n"
                "- Visible by following customers: employees see everything;\n"
                "   if website is activated, portal users may see project, tasks or issues followed by\n"
                "   them or by someone of their company\n")
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    date_start = fields.Date(string='Start Date')
    date = fields.Date(string='Expiration Date', index=True, track_visibility='onchange')
    subtask_project_id = fields.Many2one('project.project', string='Sub-task Project', ondelete="restrict",
        help="Choosing a sub-tasks project will both enable sub-tasks and set their default project (possibly the project itself)")

    _sql_constraints = [
        ('project_date_greater', 'check(date >= date_start)', 'Error! project start-date must be lower than project end-date.')
    ]

    def _compute_portal_url(self):
        super(Project, self)._compute_portal_url()
        for project in self:
            project.portal_url = '/my/project/%s' % project.id

    @api.multi
    def map_tasks(self, new_project_id):
        """ copy and map tasks from old to new project """
        # We want to copy archived task, but do not propagate an active_test context key
        task_ids = self.env['project.task'].with_context(active_test=False).search([('project_id', '=', self.id)], order='parent_id').ids
        old_to_new_tasks = {}
        for task in self.env['project.task'].browse(task_ids):
            # preserve task name and stage, normally altered during copy
            defaults = {'stage_id': task.stage_id.id,
                        'name': task.name}
            parent_id = old_to_new_tasks.get(task.parent_id.id, False) if task.parent_id else False
            project_id = (new_project_id if not parent_id else
                          self.env['project.project'].browse(new_project_id).subtask_project_id.id)
            defaults['parent_id'] = parent_id
            defaults['project_id'] = project_id
            new_task = task.copy(defaults)
            old_to_new_tasks[task.id] = new_task.id
        return True

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % (self.name)
        project = super(Project, self).copy(default)
        if self.subtask_project_id == self:
            project.subtask_project_id = project
        for follower in self.message_follower_ids:
            project.message_subscribe(partner_ids=follower.partner_id.ids, subtype_ids=follower.subtype_ids.ids)
        if 'tasks' not in default:
            self.map_tasks(project.id)
        return project

    @api.model
    def create(self, vals):
        # Prevent double project creation
        self = self.with_context(mail_create_nosubscribe=True)

        project = super(Project, self).create(vals)
        project.write({"plantilla2021":True})
        if not vals.get('subtask_project_id'):
            project.subtask_project_id = project.id
        if project.privacy_visibility == 'portal' and project.partner_id:
            project.message_subscribe(project.partner_id.ids)
        #fields.Selection([ ('platillagenerales', 'ADMINISTACIÓN DE PROYECTOS GENERALES'),('platillafabricacion', 'ADMINISTRACIÓN DE PROYECTOS DE FABRICACIÓN'),('platillatareas', 'ADMINISTRACIÓN DE TAREAS')])
        etapas=""
        tasks=""
        
        if str(project.plantilla) =='platillagenerales':
            project.write({"name": str("ADMINISTACIÓN DE PROYECTOS GENERALES("+str(project.name)+")")})
            ids_etapas=[231,232,233,234,235,236,237,238,239]
            etapas="("+str(ids_etapas[0])+","+str(project.id)+"),"+"("+str(ids_etapas[1])+","+str(project.id)+"),"+"("+str(ids_etapas[2])+","+str(project.id)+"),"+"("+str(ids_etapas[3])+","+str(project.id)+"),"+"("+str(ids_etapas[4])+","+str(project.id)+"),"+"("+str(ids_etapas[5])+","+str(project.id)+"),"+"("+str(ids_etapas[6])+","+str(project.id)+"),"+"("+str(ids_etapas[7])+","+str(project.id)+"),"+"("+str(ids_etapas[8])+","+str(project.id)+");" #+str(project.id)+")"+"("+str(ids_etapas[8])++"("+str(ids_etapas[8])++"("+str(ids_etapas[8])++"("+str(ids_etapas[8])+


        if str(project.plantilla) =='platillafabricacion':
            #Proyectos de Fabricación        
            ids_etapas=[240,241,242,243,244,245,246,247]
            etapas="("+str(ids_etapas[0])+","+str(project.id)+"),"+"("+str(ids_etapas[1])+","+str(project.id)+"),"+"("+str(ids_etapas[2])+","+str(project.id)+"),"+"("+str(ids_etapas[3])+","+str(project.id)+"),"+"("+str(ids_etapas[4])+","+str(project.id)+"),"+"("+str(ids_etapas[5])+","+str(project.id)+"),"+"("+str(ids_etapas[6])+","+str(project.id)+"),"+"("+str(ids_etapas[7])+","+str(project.id)+");"
            project.write({"name": str("ADMINISTRACIÓN DE PROYECTOS DE FABRICACIÓN("+str(project.name)+")")})
            tasks="INSERT INTO public.project_task (active,name,description,stage_id,kanban_state,project_id,plantilla2021) VALUES \
            (true,'CARGA DE PEDIDO EN ODOO','<p>Registrar y/o actualizar proyecto en Sistema Odoo para el correcto manejo de la información de manera interna y para la correcta facturación de pedido cuando sea necesario.</p>',"+str(ids_etapas[0])+",'normal',"+str(project.id)+",true), \
            (true,'PRESENTACIÓN DE PROYECTO','<p>Coordinar la presentación del proyecto.</p><p>   *Enviar invitación vía correo electrónico a los involucrados de cada área, indicando fecha y horario de la misma, y adjuntando información relevante al proyecto (#pedido en Odoo, Voz de cliente, Hoja de proyecto, Orden de compra...)</p><p>    *En la presentación, tomar nota sobre proyecto para la elaboración de plan de proyecto (actualización de actividades)</p>',"+str(ids_etapas[0])+",'normal',"+str(project.id)+",true), \
            (true,'VALIDACIÓN DE PROTOTIPO','<p> </p>',"+str(ids_etapas[0])+",'normal',"+str(project.id)+",true), \
            (true,'TIMING DEL PROYECTO','<p> </p>',"+str(ids_etapas[1])+",'normal',"+str(project.id)+",true), \
            (true,'PROGRAMACIÓN DE MANUFACTURAS','<p>Se programarán MO´s de acuerdo a Plan Maestro de Producción, mismas que se colocarán en el Plan de Supervisores</p>',"+str(ids_etapas[1])+",'normal',"+str(project.id)+",true), \
            (true,'IDENTIFICACIÓN DE PROCESOS CRÍTICOS','<p> </p>',"+str(ids_etapas[1])+",'normal',"+str(project.id)+",true), \
            (true,'DIBUJOS DE FABRICACIÓN','<p>Elabora dibujos para fabricación (pantógrafos)</p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'SET UP DE PROCESOS CRÍTICOS','<p> </p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'LISTA DE MATERIALES','<p>Elaboración y carga de la lista de materiales en el sistema</p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'DISEÑO CONCEPTUAL','<p> </p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'DISEÑO ESPECÍFICO','<p> </p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'IMPORTACIÓN DE PIEZAS DEL CLIENTE','<p> </p>',"+str(ids_etapas[3])+",'normal',"+str(project.id)+",true), \
            (true,'COMPRA DE MATERIAL PARA PROTOTIPO','<p> </p>',"+str(ids_etapas[3])+",'normal',"+str(project.id)+",true), \
            (true,'COMPRA DE MATERIALES CRÍTICOS','<p></p>',"+str(ids_etapas[3])+",'normal',"+str(project.id)+",true), \
            (true,'IMPORTACIÓN DE MATERIALES','<p></p>',"+str(ids_etapas[3])+",'normal',"+str(project.id)+",true),  \
            (true,'COMPRA Y ARRIBO DE MATERIALES PARA PROTOTIPO Y ESCANTILLONES','<p></p>',"+str(ids_etapas[3])+",'normal',"+str(project.id)+",true),  \
            (true,'COMPRA DE MATERIAL PARA INICIO DE PRODUCCIÓN','<p></p>',"+str(ids_etapas[3])+",'normal',"+str(project.id)+",true), \
            (true,'FABRICACIÓN DE ESCANTILLONES','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'ARRANQUE DE FABRICACIÓN','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'FABRICACIÓN DE PROTOTIPO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'FABRICACIÓN DE PRIMERA PIEZA','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true),  \
            (true,'DEFINICIÓN DE PLAN DE CONTROL','<p></p>',"+str(ids_etapas[5])+",'normal',"+str(project.id)+",true), \
            (true,'DESPLIEGUE DEL PLAN DE CONTROL','<p></p>',"+str(ids_etapas[5])+",'normal',"+str(project.id)+",true), \
            (true,'PLAN DE CONTROL','<p></p>',"+str(ids_etapas[5])+",'normal',"+str(project.id)+",true), \
            (true,'VALIDACIÓN DE PRIMERA PIEZA','<p></p>',"+str(ids_etapas[0])+",'normal',"+str(project.id)+",true), \
            (true,'MODELADO DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'DEFINICIÓN DE SOLDADURA','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'DEFINICIÓN DE TOLERANCIAS Y CARACTERISTICAS CRITICAS DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'JUNTA CONCURRENTE DE PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'ACTUALIZAR DISEÑO EN BASE A OBSERVACIONES DE LA JUNTA','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'GENERAR Y ENVIAR LISTA DE IMPORTACIONES Y MATERIALES CRITICOS','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'LISTA DE MATERIALES DEL PRODUCTO PARA PROTOTIPO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REVISIÓN Y LIBERACIÓN DE LISTA DE MATERIALES PARA PROTOTIPO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'CAPTURA DE LISTA DE MATERIALES A ODOO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'LISTAS DE CORTE Y HABILITADOS Y DISTRIBUCIONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REALIZAR PLANOS DE MANUFACTURA DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'VALIDAR QUE LOS DISEÑOS SE ACTUALICEN AL 100 %','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'CNC DE PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REVISIÓN Y FIRMA DE DIBUJOS DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'MODELADO DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'DEFINICIÓN DE SOLDADURA','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'DEFINICIÓN DE TOLERANCIAS Y CARACTERISTICAS CRITICAS DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'JUNTA CONCURRENTE DE PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'ACTUALIZAR DISEÑO EN BASE A OBSERVACIONES DE LA JUNTA','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'GENERAR Y ENVIAR LISTA DE IMPORTACIONES Y MATERIALES CRITICOS','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'LISTA DE MATERIALES DEL PRODUCTO PARA PROTOTIPO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REVISIÓN Y LIBERACIÓN DE LISTA DE MATERIALES PARA PROTOTIPO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'CAPTURA DE LISTA DE MATERIALES A ODOO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'LISTAS DE CORTE Y HABILITADOS Y DISTRIBUCIONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REALIZAR PLANOS DE MANUFACTURA DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'VALIDAR QUE LOS DISEÑOS SE ACTUALICEN AL 100 %','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'CNC DE PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REVISIÓN Y FIRMA DE DIBUJOS DEL PRODUCTO','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'ANALISIS DE LOS TIEMPOS DE ARMADO (para definir cantidad de escantillones a producir)','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'LISTA DE ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'DISEÑO DE LOS ESCANTILLONES, PLANTILLAS Y PASA NO PASA','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'PROPUESTA DE LAY OUT PARA MONTAJE EN LÍNEA','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'JUNTA CONCURRENTE DE ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'LISTA DE MATERIALES DE ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REVISIÓN Y LIBERACIÓN DE LISTAS DE MATERIALES PARA ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'ACTUALIZAR DISEÑO DE ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'REVISIÓN Y FIRMA DE DIBUJOS DE ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'PLANOS DE MANUFACTURA ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'CNC DE ESCANTILLONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'ACTUALIZACIÓN DE DISEÑOS EN BASE A VALIDACIONES','<p></p>',"+str(ids_etapas[2])+",'normal',"+str(project.id)+",true), \
            (true,'CORTE Y HABILITADO DE PROTOTIPO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'ARMADO DE PROTOTIPO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'PINTURA Y VESTIDURA DE PROTOTIPO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'VALIDACIÓN DE PROTOTIPO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'VALIDACIÓN DE CONSUMOS (PINTURA/PEGAMENTOS/RECUBRIMIENTOS)','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'CORTE Y HABILITADO DE MATERIAL PARA ESCANTILLONES','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'FABRICACION DE ESCANTILLONES','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'FABRICACIÓN PILOTO ESTATICO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'MONTAJE DEL PROCESO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'FABRICACIÓN PILOTO DINÁMICO','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'VALIDACIÓN DE MONTAJES','<p></p>',"+str(ids_etapas[4])+",'normal',"+str(project.id)+",true), \
            (true,'ENTREGA DE PRIMERA PIEZA','<p></p>', "+str(ids_etapas[6])+", 'normal', "+str(project.id)+",true);"


          
# ... (continuar con las subtareas)



        # print(tasks)
        if str(project.plantilla) =='platillatareas':
            #Tareas
            ids_etapas=[248,249,250,251]
            etapas="("+str(ids_etapas[0])+","+str(project.id)+"),"+"("+str(ids_etapas[1])+","+str(project.id)+"),"+"("+str(ids_etapas[2])+","+str(project.id)+"),"+"("+str(ids_etapas[3])+","+str(project.id)+")"
        if not project.plantilla:
            raise UserError(_("Por Favor selecciona una plantilla, o pide ayuda al administrador para crear una plantilla nueva"))
        query='INSERT INTO public.project_task_type_rel (type_id, project_id) VALUES '+etapas
        # print(query)
        project._cr.execute(query)
        if tasks:
            project._cr.execute(tasks)

        return project

    @api.multi
    def write(self, vals):
        # directly compute is_favorite to dodge allow write access right
        if 'is_favorite' in vals:
            vals.pop('is_favorite')
            self._fields['is_favorite'].determine_inverse(self)
        res = super(Project, self).write(vals) if vals else True
        if 'active' in vals:
            # archiving/unarchiving a project does it on its tasks, too
            self.with_context(active_test=False).mapped('tasks').write({'active': vals['active']})
            # archiving/unarchiving a project implies that we don't want to use the analytic account anymore
            self.with_context(active_test=False).mapped('analytic_account_id').write({'active': vals['active']})
        if vals.get('partner_id') or vals.get('privacy_visibility'):
            for project in self.filtered(lambda project: project.privacy_visibility == 'portal'):
                project.message_subscribe(project.partner_id.ids)
        return res

    @api.multi
    def get_access_action(self, access_uid=None):
        """ Instead of the classic form view, redirect to website for portal users
        that can read the project. """
        self.ensure_one()
        user, record = self.env.user, self
        if access_uid:
            user = self.env['res.users'].sudo().browse(access_uid)
            record = self.sudo(user)

        if user.share:
            try:
                record.check_access_rule('read')
            except AccessError:
                pass
            else:
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/my/project/%s' % self.id,
                    'target': 'self',
                    'res_id': self.id,
                }
        return super(Project, self).get_access_action(access_uid)

    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        """ Subscribe to all existing active tasks when subscribing to a project """
        res = super(Project, self).message_subscribe(partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids, force=force)
        if not subtype_ids or any(subtype.parent_id.res_model == 'project.task' for subtype in self.env['mail.message.subtype'].browse(subtype_ids)):
            for partner_id in partner_ids or []:
                self.mapped('tasks').filtered(lambda task: not task.stage_id.fold and partner_id not in task.message_partner_ids.ids).message_subscribe(
                    partner_ids=[partner_id], channel_ids=None, subtype_ids=None, force=False)
            for channel_id in channel_ids or []:
                self.mapped('tasks').filtered(lambda task: not task.stage_id.fold and channel_id not in task.message_channel_ids.ids).message_subscribe(
                    partner_ids=None, channel_ids=[channel_id], subtype_ids=None, force=False)
        return res

    @api.multi
    def message_unsubscribe(self, partner_ids=None, channel_ids=None):
        """ Unsubscribe from all tasks when unsubscribing from a project """
        self.mapped('tasks').message_unsubscribe(partner_ids=partner_ids, channel_ids=channel_ids)
        return super(Project, self).message_unsubscribe(partner_ids=partner_ids, channel_ids=channel_ids)

    @api.multi
    def _notification_recipients(self, message, groups):
        groups = super(Project, self)._notification_recipients(message, groups)

        for group_name, group_method, group_data in groups:
            if group_name in ['customer', 'portal']:
                continue
            group_data['has_button_access'] = True

        return groups

    @api.multi
    def toggle_favorite(self):
        favorite_projects = not_fav_projects = self.env['project.project'].sudo()
        for project in self:
            if self.env.user in project.favorite_user_ids:
                favorite_projects |= project
            else:
                not_fav_projects |= project

        # Project User has no write access for project.
        not_fav_projects.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_projects.write({'favorite_user_ids': [(3, self.env.uid)]})

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def edit_dialog(self):
        form_view = self.env.ref('project.edit_project')
        return {
            'name': _('Project'),
            'res_model': 'project.project',
            'res_id': self.id,
            'views': [(form_view.id, 'form'),],
            'type': 'ir.actions.act_window',
            'target': 'inline'
        }


class Task(models.Model):
    _name = "project.task"
    _description = "Task"
    _date_name = "date_start"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = "priority desc, sequence, id desc"

    def _get_default_partner(self):
        if 'default_project_id' in self.env.context:
            default_project_id = self.env['project.project'].browse(self.env.context['default_project_id'])
            return default_project_id.exists().partner_id

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    active = fields.Boolean(default=True)
    plantilla2021 = fields.Boolean(help="it works to know that the record is new, this so that the on_move_task method does not direct it to the error when creating")
    name = fields.Char(string='Task Title', track_visibility='always', required=True, index=True)
    description = fields.Html(string='Description')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ], default='0', index=True, string="Priority")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tasks.")
    stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
        default=_get_default_stage_id, group_expand='_read_group_stage_ids',
        domain="[('project_ids', '=', project_id)]", copy=False)
    tag_ids = fields.Many2many('project.tags', string='Tags', oldname='categ_ids')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True,
        help="A task's kanban state indicates special situations affecting it:\n"
             " * Grey is the default situation\n"
             " * Red indicates something is preventing the progress of this task\n"
             " * Green indicates the task is ready to be pulled to the next stage")
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State', track_visibility='onchange')
    create_date = fields.Datetime(index=True)
    write_date = fields.Datetime(index=True)  #not displayed in the view but it might be useful with base_automation module (and it needs to be defined first for that)
    date_start = fields.Datetime(string='Starting Date',
    default=fields.Datetime.now,
    index=True, copy=False)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
        default=fields.Datetime.now,
        index=True,
        copy=False,
        readonly=True)
    project_id = fields.Many2one('project.project',
        string='Project',
        default=lambda self: self.env.context.get('default_project_id'),
        index=True,
        track_visibility='onchange',
        change_default=True)
    notes = fields.Text(string='Notes')
    planned_hours = fields.Float(string='Initially Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.')
    remaining_hours = fields.Float(string='Remaining Hours', digits=(16,2), help="Total remaining time, can be re-estimated periodically by the assignee of the task.")
    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
        string='Customer',
        default=_get_default_partner)
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True, related_sudo=False)
    company_id = fields.Many2one('res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    color = fields.Integer(string='Color Index')
    user_email = fields.Char(related='user_id.email', string='User Email', readonly=True, related_sudo=False)
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
        help="Attachment that don't come from message.")
    # In the domain of displayed_image_id, we couln't use attachment_ids because a one2many is represented as a list of commands so we used res_model & res_id
    displayed_image_id = fields.Many2one('ir.attachment', domain="[('res_model', '=', 'project.task'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]", string='Cover Image')
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    parent_id = fields.Many2one('project.task', string='Parent Task', index=True)
    child_ids = fields.One2many('project.task', 'parent_id', string="Sub-tasks", context={'active_test': False})
    subtask_project_id = fields.Many2one('project.project', related="project_id.subtask_project_id", string='Sub-task Project', readonly=True)
    subtask_count = fields.Integer(compute='_compute_subtask_count', type='integer', string="Sub-task count")
    email_from = fields.Char(string='Email', help="These people will receive email.", index=True)
    email_cc = fields.Char(string='Watchers Emails', help="""These email addresses will be added to the CC field of all inbound
        and outbound emails for this record before being sent. Separate multiple email addresses with a comma""")
    # Computed field about working time elapsed between record creation and assignation/closing.
    working_hours_open = fields.Float(compute='_compute_elapsed', string='Working hours to assign', store=True, group_operator="avg")
    working_hours_close = fields.Float(compute='_compute_elapsed', string='Working hours to close', store=True, group_operator="avg")
    working_days_open = fields.Float(compute='_compute_elapsed', string='Working days to assign', store=True, group_operator="avg")
    working_days_close = fields.Float(compute='_compute_elapsed', string='Working days to close', store=True, group_operator="avg")
    # customer portal: include comment and incoming emails in communication history
    website_message_ids = fields.One2many(domain=lambda self: [('model', '=', self._name), ('message_type', 'in', ['email', 'comment'])])

    def _compute_attachment_ids(self):
        for task in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', task.id), ('res_model', '=', 'project.task')]).ids
            message_attachment_ids = task.mapped('message_ids.attachment_ids').ids  # from mail_thread
            task.attachment_ids = list(set(attachment_ids) - set(message_attachment_ids))

    @api.constrains('stage_id')
    def on_move_task(self):
        if self.project_id.plantilla2021: #Si no es plantilla de 2021 no va a hacer nada
            if self.plantilla2021:#Si se crea una tarea nueva es para que no redirija a error
                if self.project_id.plantilla2021:
                    if self.project_id.plantilla:
                        if str(self.project_id.plantilla)=='platillafabricacion':
                            if int(self.stage_id.id)==247 or int(self.stage_id.id)==251:
                                print("Movido")
                            else:
                                raise UserError(_("Solo puedes mover a FINALIZADO"))
            else:
                self.write({"plantilla2021":True})


    @api.multi
    @api.depends('create_date', 'date_end', 'date_assign')
    def _compute_elapsed(self):
        task_linked_to_calendar = self.filtered(
            lambda task: task.project_id.resource_calendar_id and task.create_date
        )
        for task in task_linked_to_calendar:
            dt_create_date = fields.Datetime.from_string(task.create_date)

            if task.date_assign:
                dt_date_assign = fields.Datetime.from_string(task.date_assign)
                task.working_hours_open = task.project_id.resource_calendar_id.get_work_hours_count(
                        dt_create_date, dt_date_assign, False, compute_leaves=True)
                task.working_days_open = task.working_hours_open / 24.0

            if task.date_end:
                dt_date_end = fields.Datetime.from_string(task.date_end)
                task.working_hours_close = task.project_id.resource_calendar_id.get_work_hours_count(
                    dt_create_date, dt_date_end, False, compute_leaves=True)
                task.working_days_close = task.working_hours_close / 24.0

        (self - task_linked_to_calendar).update(dict.fromkeys(
            ['working_hours_open', 'working_hours_close', 'working_days_open', 'working_days_close'], 0.0))

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    def _compute_portal_url(self):
        super(Task, self)._compute_portal_url()
        for task in self:
            task.portal_url = '/my/task/%s' % task.id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.email_from = self.partner_id.email

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            if self.project_id.partner_id:
                self.partner_id = self.project_id.partner_id
            if self.project_id not in self.stage_id.project_ids:
                self.stage_id = self.stage_find(self.project_id.id, [('fold', '=', False)])
        else:
            self.stage_id = False

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.date_start = fields.Datetime.now()

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % self.name
        if 'remaining_hours' not in default:
            default['remaining_hours'] = self.planned_hours
        return super(Task, self).copy(default)

    @api.multi
    def _compute_subtask_count(self):
        for task in self:
            task.subtask_count = self.search_count([('id', 'child_of', task.id), ('id', '!=', task.id)])

    @api.constrains('parent_id')
    def _check_parent_id(self):
        for task in self:
            if not task._check_recursion():
                raise ValidationError(_('Error! You cannot create recursive hierarchy of task(s).'))

    @api.constrains('parent_id')
    def _check_subtask_project(self):
        for task in self:
            if task.parent_id.project_id and task.project_id != task.parent_id.project_id.subtask_project_id:
                raise UserError(_("You can't define a parent task if its project is not correctly configured. The sub-task's project of the parent task's project should be this task's project"))

    # Override view according to the company definition
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # read uom as admin to avoid access rights issues, e.g. for portal/share users,
        # this should be safe (no context passed to avoid side-effects)
        obj_tm = self.env.user.company_id.project_time_mode_id
        tm = obj_tm and obj_tm.name or 'Hours'

        res = super(Task, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        # read uom as admin to avoid access rights issues, e.g. for portal/share users,
        # this should be safe (no context passed to avoid side-effects)
        obj_tm = self.env.user.company_id.project_time_mode_id
        # using get_object to get translation value
        uom_hour = self.env.ref('product.product_uom_hour', False)
        if not obj_tm or not uom_hour or obj_tm.id == uom_hour.id:
            return res

        eview = etree.fromstring(res['arch'])

        # if the project_time_mode_id is not in hours (so in days), display it as a float field
        def _check_rec(eview):
            if eview.attrib.get('widget', '') == 'float_time':
                eview.set('widget', 'float')
            for child in eview:
                _check_rec(child)
            return True

        _check_rec(eview)

        res['arch'] = etree.tostring(eview, encoding='unicode')

        # replace reference of 'Hours' to 'Day(s)'
        for f in res['fields']:
            # TODO this NOT work in different language than english
            # the field 'Initially Planned Hours' should be replaced by 'Initially Planned Days'
            # but string 'Initially Planned Days' is not available in translation
            if 'Hours' in res['fields'][f]['string']:
                res['fields'][f]['string'] = res['fields'][f]['string'].replace('Hours', obj_tm.name)
        return res

    @api.model
    def get_empty_list_help(self, help):
        self = self.with_context(
            empty_list_help_id=self.env.context.get('default_project_id'),
            empty_list_help_model='project.project',
            empty_list_help_document_name=_("tasks")
        )
        return super(Task, self).get_empty_list_help(help)

    # ----------------------------------------
    # Case management
    # ----------------------------------------

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    # ------------------------------------------------
    # CRUD overrides
    # ------------------------------------------------

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # for default stage
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = fields.Datetime.now()
        # Stage change: Update date_end if folded stage
        if vals.get('stage_id'):
            vals.update(self.update_date_end(vals['stage_id']))
        task = super(Task, self.with_context(context)).create(vals)
        return task

    @api.multi
    def write(self, vals):
        now = fields.Datetime.now()
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals.update(self.update_date_end(vals['stage_id']))
            vals['date_last_stage_update'] = now
            # reset kanban state when changing stage
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
        # user_id change: update date_assign
        if vals.get('user_id') and 'date_assign' not in vals:
            vals['date_assign'] = now

        result = super(Task, self).write(vals)

        return result

    def update_date_end(self, stage_id):
        project_task_type = self.env['project.task.type'].browse(stage_id)
        if project_task_type.fold:
            return {'date_end': fields.Datetime.now()}
        return {'date_end': False}

    @api.multi
    def get_access_action(self, access_uid=None):
        """ Instead of the classic form view, redirect to website for portal users
        that can read the task. """
        self.ensure_one()
        user, record = self.env.user, self
        if access_uid:
            user = self.env['res.users'].sudo().browse(access_uid)
            record = self.sudo(user)

        if user.share:
            try:
                record.check_access_rule('read')
            except AccessError:
                pass
            else:
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/my/task/%s' % self.id,
                    'target': 'self',
                    'res_id': self.id,
                }
        return super(Task, self).get_access_action(access_uid)

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(Task, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value_ids = tracking[test_task.id]
        if 'stage_id' in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id, {'composition_mode': 'mass_mail'})
        return res

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'kanban_state_label' in init_values and self.kanban_state == 'blocked':
            return 'project.mt_task_blocked'
        elif 'kanban_state_label' in init_values and self.kanban_state == 'done':
            return 'project.mt_task_ready'
        elif 'user_id' in init_values and self.user_id:  # assigned -> new
            return 'project.mt_task_new'
        elif 'stage_id' in init_values and self.stage_id and self.stage_id.sequence <= 1:  # start stage -> new
            return 'project.mt_task_new'
        elif 'stage_id' in init_values:
            return 'project.mt_task_stage'
        return super(Task, self)._track_subtype(init_values)

    @api.multi
    def _notification_recipients(self, message, groups):
        """ Handle project users and managers recipients that can convert assign
        tasks and create new one directly from notification emails. """
        groups = super(Task, self)._notification_recipients(message, groups)

        self.ensure_one()
        if not self.user_id:
            take_action = self._notification_link_helper('assign')
            project_actions = [{'url': take_action, 'title': _('I take it')}]
        else:
            project_actions = []

        new_group = (
            'group_project_user', lambda partner: bool(partner.user_ids) and any(user.has_group('project.group_project_user') for user in partner.user_ids), {
                'actions': project_actions,
            })

        groups = [new_group] + groups
        for group_name, group_method, group_data in groups:
            if group_name == 'customer':
                continue
            group_data['has_button_access'] = True

        return groups

    @api.model
    def message_get_reply_to(self, res_ids, default=None):
        """ Override to get the reply_to of the parent project. """
        tasks = self.sudo().browse(res_ids)
        project_ids = tasks.mapped('project_id').ids
        aliases = self.env['project.project'].message_get_reply_to(project_ids, default=default)
        return {task.id: aliases.get(task.project_id.id, False) for task in tasks}

    @api.multi
    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        aliases = self.mapped('project_id.alias_name')
        return [x for x in email_list if x.split('@')[0] not in aliases]

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        create_context = dict(self.env.context or {})
        create_context['default_user_id'] = False
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'planned_hours': 0.0,
            'partner_id': msg.get('author_id')
        }
        defaults.update(custom_values)

        task = super(Task, self.with_context(create_context)).message_new(msg, custom_values=defaults)
        email_list = task.email_split(msg)
        partner_ids = [p for p in task._find_partner_from_emails(email_list, force_create=False) if p]
        task.message_subscribe(partner_ids)
        return task

    @api.multi
    def message_update(self, msg, update_vals=None):
        """ Override to update the task according to the email. """
        if update_vals is None:
            update_vals = {}
        maps = {
            'cost': 'planned_hours',
        }
        for line in msg['body'].split('\n'):
            line = line.strip()
            res = tools.command_re.match(line)
            if res:
                match = res.group(1).lower()
                field = maps.get(match)
                if field:
                    try:
                        update_vals[field] = float(res.group(2).lower())
                    except (ValueError, TypeError):
                        pass

        email_list = self.email_split(msg)
        partner_ids = [p for p in self._find_partner_from_emails(email_list, force_create=False) if p]
        self.message_subscribe(partner_ids)
        return super(Task, self).message_update(msg, update_vals=update_vals)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(Task, self).message_get_suggested_recipients()
        for task in self:
            if task.partner_id:
                reason = _('Customer Email') if task.partner_id.email else _('Customer')
                task._message_add_suggested_recipient(recipients, partner=task.partner_id, reason=reason)
            elif task.email_from:
                task._message_add_suggested_recipient(recipients, email=task.email_from, reason=_('Customer Email'))
        return recipients

    @api.multi
    def message_get_email_values(self, notif_mail=None):
        res = super(Task, self).message_get_email_values(notif_mail=notif_mail)
        headers = {}
        if res.get('headers'):
            try:
                headers.update(safe_eval(res['headers']))
            except Exception:
                pass
        if self.project_id:
            current_objects = [h for h in headers.get('X-Odoo-Objects', '').split(',') if h]
            current_objects.insert(0, 'project.project-%s, ' % self.project_id.id)
            headers['X-Odoo-Objects'] = ','.join(current_objects)
        if self.tag_ids:
            headers['X-Odoo-Tags'] = ','.join(self.tag_ids.mapped('name'))
        res['headers'] = repr(headers)
        return res

    def _message_post_after_hook(self, message):
        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(Task, self)._message_post_after_hook(message)

    def action_assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def action_open_parent_task(self):
        return {
            'name': _('Parent Task'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'res_id': self.parent_id.id,
            'type': 'ir.actions.act_window'
        }

    def action_subtask(self):
        action = self.env.ref('project.project_task_action_sub_task').read()[0]
        ctx = self.env.context.copy()
        ctx.update({
            'default_parent_id' : self.id,
            'default_project_id' : self.env.context.get('project_id', self.subtask_project_id.id),
            'default_name' : self.env.context.get('name', self.name) + ':',
            'default_partner_id' : self.env.context.get('partner_id', self.partner_id.id),
            'search_default_project_id': self.env.context.get('project_id', self.subtask_project_id.id),
        })
        action['context'] = ctx
        action['domain'] = [('id', 'child_of', self.id), ('id', '!=', self.id)]
        return action


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    company_uom_id = fields.Many2one('product.uom', related='company_id.project_time_mode_id', string="Company UOM")
    project_ids = fields.One2many('project.project', 'analytic_account_id', string='Projects')
    project_count = fields.Integer(compute='_compute_project_count', string='Project Count')

    def _compute_project_count(self):
        for account in self:
            account.project_count = len(account.with_context(active_test=False).project_ids)

    @api.multi
    def unlink(self):
        projects = self.env['project.project'].search([('analytic_account_id', 'in', self.ids)])
        has_tasks = self.env['project.task'].search_count([('project_id', 'in', projects.ids)])
        if has_tasks:
            raise UserError(_('Please remove existing tasks in the project linked to the accounts you want to delete.'))
        return super(AccountAnalyticAccount, self).unlink()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if self.env.context.get('current_model') == 'project.project':
            return self.search(args + [('name', operator, name)], limit=limit).name_get()

        return super(AccountAnalyticAccount, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.multi
    def projects_action(self):
        projects = self.with_context(active_test=False).mapped('project_ids')
        result = {
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", projects.ids]],
            "context": {"create": False},
            "name": "Projects",
        }
        if len(projects) == 1:
            result['views'] = [(False, "form")]
            result['res_id'] = projects.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

class ProjectTags(models.Model):
    """ Tags of project's tasks """
    _name = "project.tags"
    _description = "Tags of project's tasks"

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

