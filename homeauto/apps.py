
from django.contrib.admin.apps import AdminConfig

class MyAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.MyAdminSite'

from django.apps import AppConfig
import sys, logging
import multiprocessing

logger = logging.getLogger(__name__)

class Config(AppConfig):
    name = 'homeauto'
    if 'runserver' in sys.argv:

        def ready(self):
            logger.warning("HomeAuto Starting...")

            from homeauto import jobs
            jobs.start()

            import watchers.apps as watcher
            watcher.clean()
            watcher.start()

            import vivint.apps as vivint
            vivint.start()

