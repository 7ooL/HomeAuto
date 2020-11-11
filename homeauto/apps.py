from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig
from django.conf import settings
import sys, logging, threading, time

logger = logging.getLogger(__name__)

class Config(AppConfig):
    name = 'homeauto'
    if 'runserver' in sys.argv:

        def start_threads(self, t):
            t.daemon = True
            logger.info("Starting: "+t.getName())
            t.start()


        def thread_watcher(self, *args):
            while True:
                for t in args:
                    logger.info("checking "+t.getName()+", and it is alive:"+str(t.is_alive()))
                    if not t.is_alive():
                        logger.warning("Thread "+t.getName()+" is not alive")
                        self.start_threads(t)
                time.sleep(5)



        def ready(self):
            from homeauto import jobs, watcher, vivint

            jobs.start()


            threads = [ threading.Thread(name="Watchers", target=(watcher.start)),
                        threading.Thread(name="Vivint", target=(vivint.start))
                      ]
            for t in threads:
                self.start_threads(t)

            guard = threading.Thread(name="Thread Watcher", target=(self.thread_watcher), args=(threads))
            self.start_threads(guard)



class AppAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.AppAdminSite'
