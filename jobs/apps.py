from django.apps import AppConfig
import logging, sys

logger = logging.getLogger(__name__)

class JobsConfig(AppConfig):
    name = 'jobs'
    verbose_name = "Job Scheduler"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.debug('Starting Jobs App')
            import jobs.jobs as jobs
            jobs.start()


