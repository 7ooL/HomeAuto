
from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig
import sys, logging

class MyAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.MyAdminSite'

logger = logging.getLogger(__name__)

class HomeautoConfig(AppConfig):
    name = 'homeauto'
    verbose_name = "House Devices and Configuations"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.info('Starting '+self.verbose_name+' App')
            import homeauto.jobs as jobs
            jobs.start()
