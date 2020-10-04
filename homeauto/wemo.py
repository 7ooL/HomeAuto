from django.conf import settings
from homeauto.models.wemo import Wemo
import subprocess
import logging


# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


def turn_on_light(device):
    if device.enabled:
        if not device.status:
            cmd = '/usr/local/bin/wemo switch "'+device.name+ '" on'
            proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
            (out, err) = proc.communicate()
            logger.debug(cmd)
        else:
            logger.debug('device '+device.name+'('+str(device.id)+') is already on')
    else:
        logger.warning('device '+device.name+'('+str(device.id)+') not enabled')

def turn_off_light(device):
    if device.enabled:
        if not device.status:
            cmd = '/usr/local/bin/wemo switch "'+device.name+ '" off'
            proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
            (out, err) = proc.communicate()
            logger.debug(cmd)
        else:
            logger.debug('device '+device.name+'('+str(device.id)+') is already off')
    else:
        logger.warning('device '+device.name+'('+str(device.id)+') not enabled')


def sync_wemo():
    # get Wemo account
    from distutils.spawn import find_executable

    if find_executable('wemo') is not None:
        logger.debug("'Wemo' command exists")
        logger.debug("Syncing Wemo Data")
        cmd = '/usr/local/bin/wemo status'
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
        (out, err) = proc.communicate()
        if out:
            devices = out.rstrip(b'\n').decode()
            devices = devices.replace(")","")
            devices = devices.replace("(","")
            devices = devices.replace("'","")
            devices = devices.replace(":","")
            devices = devices.split('\n')

            x = 0
            for device in devices:
                devices[x] = device.split(',')
                y = 0
                for item in devices[x]:
                    devices[x][y] = item.strip()
                    y = y + 1
                x = x + 1

            #  all_entries = Wemo.objects.all()
            for device in devices:
                if not Wemo.objects.filter(name=device[1]).exists():
                    logger.debug("Name: "+str(device[1])+" does not exist")
                    add(device)
                else:
                    xWemo =  Wemo.objects.get(name=device[1])
                    if xWemo.type != device[0] :
                        logger.debug("Updating type for "+ str(device[1])+": "+str(device[3]))
                        xWemo.type = device[0]
                        xWemo.save()
                    if xWemo.status != int(device[3]) :
                        logger.debug("Updating status for "+ str(device[1])+": "+str(device[3]))
                        xWemo.status = device[3]
                        xWemo.save()
        else:
            logger.warning("'wemo status' command returned empty string")

    else:
        logger.error("Cannot sync Wemo data because no Account information for 'Wemo' exist")



