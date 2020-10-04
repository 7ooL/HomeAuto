from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig
from django.conf import settings
import sys
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Config(AppConfig):
    name = 'homeauto'

    if 'runserver' in sys.argv:
        def ready(self):
#            from homeauto import services
#            services.start()
            from homeauto import jobs
            jobs.start()
            from homeauto import vivint
            vivint.start()

class AppAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.AppAdminSite'
