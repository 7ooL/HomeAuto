from django.apps import AppConfig
import sys, logging

logger = logging.getLogger(__name__)

class DecorasConfig(AppConfig):
    name = 'decora'
    verbose_name = "Leviton Decora Smart"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.debug('Starting '+self.verbose_name+' App')
            import decora.jobs as jobs
            jobs.start()

