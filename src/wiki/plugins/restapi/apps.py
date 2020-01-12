from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RestApiConfig(AppConfig):
    name = 'wiki.plugins.restapi'
    verbose_name = _("Wiki REST validators")
    label = 'wiki_restapi'
