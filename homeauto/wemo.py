from django.conf import settings
from homeauto.models.wemo import Wemo
import subprocess, logging
from homeauto.admin_logs import log_addition, log_change, log_deletion

logger = logging.getLogger(__name__)

def turn_on_light(device):
    if device.enabled:
        if not device.status:
            cmd = '/usr/local/bin/wemo switch "' + device.name + '" on'
            proc = subprocess.Popen([cmd], stdout=(subprocess.PIPE), shell=True)
            out, err = proc.communicate()
            logger.info(cmd+"-"+str(device.id))
            return True
        else:
            logger.debug('device ' + device.name + '(' + str(device.id) + ') is already on')
    else:
        logger.warning('device ' + device.name + '(' + str(device.id) + ') not enabled')
    return False


def turn_off_light(device):
    if device.enabled:
        if device.status:
            cmd = '/usr/local/bin/wemo switch "' + device.name + '" off'
            proc = subprocess.Popen([cmd], stdout=(subprocess.PIPE), shell=True)
            out, err = proc.communicate()
            logger.info(cmd+"-"+str(device.id))
            return True
        else:
            logger.debug('device ' + device.name + '(' + str(device.id) + ') is already off')
    else:
        logger.warning('device ' + device.name + '(' + str(device.id) + ') not enabled')
    return False


def sync_wemo():
    from distutils.spawn import find_executable
    if find_executable('wemo') is not None:
        logger.debug("'wemo' command exists")
        logger.debug('Syncing Wemo Data')
        cmd = '/usr/local/bin/wemo status'
        proc = subprocess.Popen([cmd], stdout=(subprocess.PIPE), shell=True)
        out, err = proc.communicate()
        if out:
            logger.debug(out)
            devices = out.rstrip(b'\n').decode()
            devices = devices.replace(':', '')
            devices = devices.split('\n')
            logger.debug("devices")
            logger.debug(devices)
            x = 0
            for device in devices:
                logger.debug("device")
                logger.debug(device)
                attr = []
                attr.append(device.split(' ',1)[0].strip()) # type
                logger.debug("type: "+str(attr[0]))
                attr.append(device.split(' ',1)[1].split('\t')[0].strip()) # name
                logger.debug("name: "+str(attr[1]))
                attr.append(device.split('\t')[1].strip()) # status
                logger.debug("status: "+str(attr[2]))
                devices[x] = attr
                x = x + 1
            for device in devices:
                logger.debug("device: "+str(device))
                if not Wemo.objects.filter(name=(device[1])).exists():
                    logger.debug('Name: ' + str(device[1]) + ' does not exist')
                    logger.debug(device)
                    logger.info('Creating wemo:' + device[1])
                    data = {}
                    data['status'] = device[2]
                    data['type'] = device[0]
                    data['name'] = device[1]
                    w = (Wemo.objects.create)(**data)
                    w.save()
                    log_addition(w)
                else:
                    xWemo = Wemo.objects.get(name=(device[1]))
                    if xWemo.type != device[0]:
                        logger.info('Updating type for ' + str(device[1]) + ': ' + str(device[2]))
                        xWemo.type = device[0]
                        xWemo.save()
                    if xWemo.status != int(device[2]):
                        logger.info('Updating status for ' + str(device[1]) + ': ' + str(device[2]))
                        xWemo.status = device[2]
                        xWemo.save()
        else:
            logger.warning("'wemo status' command returned empty string")
    else:
        logger.error("Cannot sync Wemo data because no Account information for 'Wemo' exist")
