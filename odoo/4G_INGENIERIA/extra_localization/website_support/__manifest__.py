{
    'name': "Website Help Desk / Support Ticket",
    'version': "1.6.9",
    'author': "Sythil Tech, Adaptive City",
    'category': "Tools",
    'summary': "A helpdesk / support ticket system for your website",
    'description': "A helpdesk / support ticket system for your website",
    'license':'LGPL-3',
    'data': [
        'data/ir.module.category.csv',
        'data/res.groups.xml',
        'views/email_templates.xml',
        'views/website_support_ticket_templates.xml',
        'views/website_support_ticket_compose_views.xml',
        'views/website_support_ticket_close_views.xml',
        'views/website_support_ticket_merge_views.xml',
        'views/website_support_ticket_views.xml',
        'views/website_support_ticket_categories_views.xml',
        'views/website_support_ticket_subcategory_views.xml',
        'views/website_support_ticket_states_views.xml',
        'views/website_support_ticket_tag_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/website_support_help_groups_views.xml',
        'views/website_support_help_page_views.xml',
        'views/website_support_ticket_priority_views.xml',
        'views/website_support_settings_views.xml',
        'views/website_support_ticket_department_views.xml',
        #'views/website_support_sla_views.xml',
        'views/menus.xml',
        'data/website_support_sequence.xml',
        'data/website.support.ticket.states.xml',
        'data/website.support.ticket.categories.xml',
        'data/website.menu.csv',
        'data/website.support.ticket.priority.xml',
        'data/website.support.settings.xml',
        'data/website.support.department.role.csv',
        'data/website.support.ticket.approval.xml',
        'data/ir.cron.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'depends': ['mail','web', 'website','resource'],
    'images':[
        'static/description/3.jpg',
        'static/description/1.jpg',
        'static/description/2.jpg',
        'static/description/4.jpg',
        'static/description/5.jpg',
        'static/description/6.jpg',
    ],
    'installable': True,
}