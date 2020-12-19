import time, logging, sys, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from homeauto.models.watcher import Directory
from homeauto.house import register_watcher_event

logger = logging.getLogger(__name__)



def clean():
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

def start():

    logger.warning("begining of watcher start")
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

        while observer.is_alive():
            time.sleep(5)

        try:
            observer.stop()
        except:
            logger.error("Unexpected error (stop):"+ str(sys.exc_info()[0]))
        try:
            observer.join()
        except:
            logger.error("Unexpected error (join):"+ str(sys.exc_info()[0]))

        logger.warning("watcher dead, try and start again")
#        start()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        register_watcher_event(event)
