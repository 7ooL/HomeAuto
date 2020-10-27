from homeauto.api_vivint.pyvivintsky.vivint_sky import VivintSky
from homeauto.models.house import Account
from homeauto.models.vivint import Panel, Device
import asyncio, logging, warnings, time
import homeauto.jobs as jobs

logger = logging.getLogger(__name__)

ACCT_NAME = 'Vivint'

def start():
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
            keep_alive(session)
        else:
            logger.warning('Cannot connect to Vivint because the account is disabled')
    else:
        logger.error('Cannot connect to Vivint because no Account information for ' + ACCT_NAME + ' exist')

def keep_alive(session):
    alive = True
    while alive:
        if session.session_valid():
            time.sleep(5)
        else:
            alive = False
    session.disconnect()
    start()

def sync_vivint_sensors():
    warnings.filterwarnings('ignore')
    if Account.objects.filter(name=ACCT_NAME).exists():
        logger.debug('Account name ' + ACCT_NAME + ' exists')
        vivintAcct = Account.objects.get(name=ACCT_NAME)
        if getattr(vivintAcct, 'enabled'):
            logger.debug('Account ' + ACCT_NAME + ' is enabled')
            session = VivintSky(vivintAcct.username, vivintAcct.password)
            asyncio.run(session.login())
            asyncio.run(session.connect_panel())
            for panel in session.get_panels():
                pdata = {}
                pdata['armed_state'] = session.get_panel(panel).get_armed_state()
                pdata['street'] = session.get_panel(panel).street()
                pdata['zip'] = session.get_panel(panel).zip_code()
                pdata['city'] = session.get_panel(panel).city()
                ID = session.get_panel(panel).id()
                pdata['id'] = ID
                pdata['name'] = 'Panel_' + str(ID)
                if not Panel.objects.filter(id=ID).exists():
                    logger.info('Creating Panel: ' + ID)
                    p = (Panel.objects.create)(**pdata)
                    p.save()
                else:
                    logger.debug('Updating Panel: ' + ID)
                    (Panel.objects.filter(id=ID).update)(**pdata)
                devices = session.get_panel(panel).get_devices()
                for device in session.get_panel(panel).get_devices():
                    ddata = {}
                    ID = session.get_panel(panel).get_device(device).id()
                    ddata['id'] = ID
                    ddata['name'] = session.get_panel(panel).get_device(device).name()
                    ddata['type'] = session.get_panel(panel).get_device(device).device_type()
                    if session.get_panel(panel).get_device(device).device_type() == 'wireless_sensor':
                        ddata['state'] = session.get_panel(panel).get_device(device).state()
                    if session.get_panel(panel).get_device(device).device_type() == 'door_lock_device':
                        ddata['state'] = session.get_panel(panel).get_device(device).state()
                    if not Device.objects.filter(id=ID).exists():
                        logger.info('Creating Device: ' + ddata['name'])
                        d = (Device.objects.create)(**ddata)
                        d.save()
                    else:
                        logger.debug('Updating Device: ' + ddata['name'])
                        (Device.objects.filter(id=ID).update)(**ddata)
        else:
            logger.warning('Cannot connect to ' + ACCT_NAME + ' because the account is disabled')
    else:
        logger.error('No account ' + ACCT_NAME + ' exist')
