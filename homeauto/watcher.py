import time, logging, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from homeauto.models.watcher import Directory
from homeauto.house import register_watcher_event

logger = logging.getLogger(__name__)

def start():

    directories = Directory.objects.all()
    if directories:
        for directory in directories:
            if directory.enabled:
                w = Watcher(directory.directory)
                w.run()
            else:
                logger.warning('Directory: ' + directory.directory + ' is not enabled')
    else:
        logger.error('Will not start watchers on directories as none exist')


class Watcher:

    def __init__(self, dir):
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = dir

    def run(self):

        event_handler = Handler()
        observer = Observer()
        observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        observer.start()
#        observer.join()
        try:
            while observer.is_alive():
                time.sleep(5)
                logger.warning("watcher sleep")
        except:
            logger.error("Unexpected error:"+ str(sys.exc_info()[0]))
        finally:
            observer.stop()
            logger.warning("watcher stopped???, try and start again")
            start()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        register_watcher_event(event)
