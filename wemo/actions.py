
import subprocess, logging

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


