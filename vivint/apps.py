from django.apps import AppConfig
from django.core.exceptions import ObjectDoesNotExist
import asyncio, logging, warnings, time, multiprocessing, sys, traceback, aiohttp

logger = logging.getLogger(__name__)

class VivintConfig(AppConfig):
    name = 'vivint'
    verbose_name = "Vivint Security System"
    if 'runserver' in sys.argv:
        def ready(self):
            logger.warning('Starting Vivint App')
            self.start()

    def start(self):
        from vivint.models import Account
        from api_vivint.pyvivintsky.vivint_sky import VivintSky
        try:
            vivintAcct = Account.objects.get(pk=1)
        except ObjectDoesNotExist as e:
            logger.error(e)
        except:
            logger.error("Error:"+ str(traceback.format_exc()))
        else:
            if vivintAcct.pubnub:
                warnings.filterwarnings('ignore')
                session = VivintSky(vivintAcct.vivint_username, vivintAcct.vivint_password)
                try:
                    asyncio.run(session.login())
                except aiohttp.ClientResponseError as e:
                    logger.error(e)
                except:
                    logger.error("Error:"+ str(traceback.format_exc()))
                else:
                    asyncio.run(session.connect_panel())
                    asyncio.run(session.connect_pubnub())
                    logger.debug("Session Expires: "+str(session.get_session()['expires']))
                    process = multiprocessing.Process(target=self.keep_alive, args=(session,), name="Vivint")
                    process.start()
            else:
                logger.warning("Vivint live events are disabled")

    def keep_alive(self, session):
        try:
            alive = True
            while alive:
                if session.session_valid():
                    time.sleep(5)
                else:
                    alive = False
            session.disconnect()
            start()
        except KeyboardInterrupt:
            logger.error('Vivint Stopped.')








