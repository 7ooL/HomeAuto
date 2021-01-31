from django.apps import AppConfig
import logging, sys

logger = logging.getLogger(__name__)

class VivintConfig(AppConfig):
    name = 'vivint'
    verbose_name = "Vivint Security System"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.debug('Starting Vivint App')
            import vivint.jobs as jobs
            jobs.start()



