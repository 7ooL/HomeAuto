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
            threads = [ threading.Thread(name="Watchers", target=(watcher.start)),
                        threading.Thread(name="Vivint", target=(vivint.start)),
                        threading.Thread(name="Jobs", target=(jobs.start))
                      ]
            for t in threads:
                t.daemon = True
                logger.info("Starting: "+t.getName())
                t.start()

class AppAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.AppAdminSite'
