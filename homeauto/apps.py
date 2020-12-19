from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig
from django.conf import settings
import sys, logging, time, traceback, threading

logger = logging.getLogger(__name__)

from threading import Thread, Event

class ReusableThread(Thread):
    """
    This class provides code for a restartale / reusable thread

    join() will only wait for one (target)functioncall to finish
    finish() will finish the whole thread (after that, it's not restartable anymore)

    """

    def __init__(self, target, name, args):
        self._startSignal = Event()
        self._oneRunFinished = Event()
        self._finishIndicator = False
        self._callable = target
        self._callableArgs = args
        self._name = name

        Thread.__init__(self, name=name)

    def restart(self):
        """make sure to always call join() before restarting"""
        logger.warning("Restarting "+self._name)
        self._startSignal.set()


    def run(self):
        """ This class will reprocess the object "processObject" forever.
        Through the change of data inside processObject and start signals
        we can reuse the thread's resources"""

        self.restart()
        while(True):
            # wait until we should process
            self._startSignal.wait()

            self._startSignal.clear()

            if(self._finishIndicator):# check, if we want to stop
                self._oneRunFinished.set()
                return

            # call the threaded function
            self._callable(*self._callableArgs)
            logger.warning("after callable")

            # notify about the run's end
            self._oneRunFinished.set()
            logger.warning("after oneRunFinished")

    def join(self):
        """ This join will only wait for one single run (target functioncall) to be finished"""
        self._oneRunFinished.wait()
        self._oneRunFinished.clear()
        logger.warning("after join")


    def finish(self):
        logger.warning("running finish")
        self._finishIndicator = True
        self.restart()
        self.join()

class Config(AppConfig):
    name = 'homeauto'
    if 'runserver' in sys.argv:

        def start_threads(self, t):
#            if not t.isDaemon():
#                t.daemon = True
            t.start()
            logger.info("Starting: "+t.getName()+" ("+str(t.ident)+")")


        def thread_watcher(self, *args):
            while True:
                for t in args:
                    if not t.is_alive():
                        logger.warning("Thread "+t.getName()+" is not alive")
                        t.join()
                        t.restart()
                        logger.warning("after join and restart")
                time.sleep(5)



        def ready(self):
            logger.warning("HomeAuto Starting...")
            from homeauto import jobs, watcher, vivint
            jobs.start()
            watcher.clean()

            threads = [ ReusableThread(target=(watcher.start), name="Watcher", args=[]),
                        ReusableThread(target=(vivint.start), name="Vivint", args=[])
                      ]

            for t in threads:
                self.start_threads(t)

            guard = threading.Thread(name="Thread Watcher", target=(self.thread_watcher), args=(threads))
            self.start_threads(guard)


class AppAdminConfig(AdminConfig):
    default_site = 'homeauto.admin.AppAdminSite'

