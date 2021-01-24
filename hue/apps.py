from django.apps import AppConfig
import sys, logging

logger = logging.getLogger(__name__)

class HuesConfig(AppConfig):
    name = 'hue'
    verbose_name = "Phillips Hue"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.debug('Starting '+self.verbose_name+' App')
            import hue.jobs as jobs
            jobs.start()


