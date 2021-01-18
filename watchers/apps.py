from django.apps import AppConfig
import time, logging, os, sys
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


logger = logging.getLogger(__name__)

class WatchersConfig(AppConfig):
    name = 'watchers'
    verbose_name = "Directory Watchers"

    if 'runserver' in sys.argv:
        def ready(self):
            logger.debug('Starting Watcher App')
            self.clean()
            self.start()

    def clean(self):
        from watchers.models import Directory
        directories = Directory.objects.all()
        if directories:
            for directory in directories:
                if directory.enabled:
                    # cleanup directory before starting
                    filelist = [ f for f in os.listdir(directory.directory) ]
                    for f in filelist:
                        os.remove(os.path.join(directory.directory, f))
                        logger.warning("cleaning up file: "+f)
                else:
                    logger.warning('Directory: ' + directory.directory + ' is not enabled')
        else:
            logger.error('Will not start watchers on directories as none exist')

    def start(self):
        from watchers.models import Directory
        directories = Directory.objects.all()
        if directories:
           for directory in directories:
                if directory.enabled:
                    logger.info("Starting Watcher on: "+directory.directory)
                    w = Watcher(directory.directory)
                    try:
                        w.run()
                    except KeyboardInterrupt:
                        logger.error('Watcher Stopped.')
                else:
                   logger.warning('Directory: ' + directory.directory + ' is not enabled')
        else:
            logger.error('Will not start watchers on directories as none exist')


class Watcher:

    def __init__(self, dir):
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = dir

    def run(self):
        observer = Observer()
        observer.schedule(event_handler=Handler('*'), path=self.DIRECTORY_TO_WATCH)
        observer.daemon = False
        try:
            observer.start()
        except KeyboardInterrupt:
            logger.error('Watcher Stopped.')
        observer.join(2)


class Handler(PatternMatchingEventHandler):

    @staticmethod
    def on_any_event(event):
        from homeauto.house import register_watcher_event
        logger.debug('New event - %s.' % event)
        if event.event_type == 'created':
            register_watcher_event(event)

