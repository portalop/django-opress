﻿"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'hispaniae.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        self.children.append(modules.AppList(
            _(u'Contenidos'),
            collapsible=True,
            column=1,
            models=('opress.*',),
        ))
        self.children.append(modules.AppList(
            _(u'Fotos'),
            collapsible=True,
            column=1,
            models=('photologue.*',),
        ))
        
        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _(u'Administración'),
            column=1,
            collapsible=True,
            models=('django.contrib.*',),
        ))
        
        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=15,
            collapsible=False,
            column=2,
        ))