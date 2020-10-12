from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig
from django.conf import settings
import sys, logging, threading

logger = logging.getLogger(__name__)

class Config(AppConfig):
    name = 'homeauto'
    if 'runserver' in sys.argv:

        def ready(self):
            from homeauto import jobs, watcher, vivint
            t1 = threading.Thread(target=(jobs.start))
            t1.daemon = True
            t1.start()
            t2 = threading.Thread(target=(watcher.start))
            t2.daemon = True
            t2.start()
            t3 = threading.Thread(target=(vivint.start))
            t3.daemon = True
            t3.start()


class AppAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.AppAdminSite'
