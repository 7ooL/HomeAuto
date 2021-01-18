
from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig
import sys, logging

class MyAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.MyAdminSite'

logger = logging.getLogger(__name__)

class Config(AppConfig):
    name = 'homeauto'
    if 'runserver' in sys.argv:

        def ready(self):
            logger.warning("HomeAuto Starting...")

            from homeauto import jobs
            jobs.start()

