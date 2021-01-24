from django.apps import AppConfig
import sys, logging

logger = logging.getLogger(__name__)

class WemosConfig(AppConfig):
    name = 'wemo'
    verbose_name = "Wemo Devices"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.debug('Starting '+self.verbose_name+' App')
            import wemo.jobs as jobs
            jobs.start()

