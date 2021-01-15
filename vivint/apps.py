from django.apps import AppConfig

class VivintConfig(AppConfig):
    name = 'vivint'

from vivint.models import Panel, Device
from api_vivint.pyvivintsky.vivint_sky import VivintSky
from homeauto.models import Account
from homeauto.event_logs import log_addition, log_change, log_deletion
import homeauto.jobs as jobs
import asyncio, logging, warnings, time, multiprocessing

logger = logging.getLogger(__name__)

ACCT_NAME = 'Vivint'

def start():
    logger.info("Starting Vivint Connection")
    warnings.filterwarnings('ignore')
    if Account.objects.filter(name=ACCT_NAME).exists():
        logger.debug('Account name ' + ACCT_NAME + ' exists')
        vivintAcct = Account.objects.get(name=ACCT_NAME)
        if getattr(vivintAcct, 'enabled'):
            logger.debug('Account ' + ACCT_NAME + ' is enabled')
            session = VivintSky(vivintAcct.username, vivintAcct.password)
            asyncio.run(session.login())
            asyncio.run(session.connect_panel())
            asyncio.run(session.connect_pubnub())
            logger.debug("Session Expires: "+str(session.get_session()['expires']))
            process = multiprocessing.Process(target=keep_alive, args=(session,), name="Vivint")
            process.start()
        else:
            logger.warning('Cannot connect to Vivint because the account is disabled')
    else:
        logger.error('Cannot connect to Vivint because no Account information for ' + ACCT_NAME + ' exist')

def keep_alive(session):
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

