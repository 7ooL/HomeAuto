from api_vivint.pyvivintsky.vivint_sky import VivintSky
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import admin
from vivint.models import Panel, Device, Account
from jobs.jobs import build_jobs
import asyncio, logging, warnings, time, multiprocessing, traceback, aiohttp
logger = logging.getLogger(__name__)

def start():
    JOBS = (
        ('Vivint', 'Get Vivint Device Status and Update Database', False, 120, sync_vivint_sensors),
    )
    build_jobs(JOBS)
    start_live_events()

def start_live_events():
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
                process = multiprocessing.Process(target=keep_alive, args=(session,), name="Vivint")
                process.start()
        else:
            logger.warning("Vivint live events are disabled")

def keep_alive(session):
    try:
        alive = True
        while alive:
            if session.session_valid():
                time.sleep(5)
            else:
                alive = False
        session.disconnect()
        start_live_events()
    except KeyboardInterrupt:
        logger.error('Vivint Stopped.')


# this is a manual update of devices and not what is received from the pubnub feed
def sync_vivint_sensors():
    try:
        vivintAcct = Account.objects.get(pk=1)
    except ObjectDoesNotExist as e:
        logger.error(e)
        logger.error('No Vivint Account information is defined')
    except:
        logger.error("Error:"+ str(traceback.format_exc()))
    else:
        warnings.filterwarnings('ignore')
        session = VivintSky(vivintAcct.vivint_username, vivintAcct.vivint_password)
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
                    log_addition(vivintAcct, d)
                else:
                    logger.debug('Updating Device: ' + ddata['name'])
                    (Device.objects.filter(id=ID).update)(**ddata)


from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

def log_addition(acct, object):
    """
    Log that an object has been successfully added.
    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, ADDITION
    LogEntry.objects.log_action(
        user_id=acct.user.id,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        object_repr=force_text(object),
        action_flag=ADDITION
    )
