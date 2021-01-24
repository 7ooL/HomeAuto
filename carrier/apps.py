from django.apps import AppConfig
import sys, logging

logger = logging.getLogger(__name__)

class CarrierConfig(AppConfig):
    name = 'carrier'
    verbose_name = "Carrier Infinity Systems"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.debug('Starting '+self.verbose_name+' App')
            import carrier.control as jobs
            jobs.start()

