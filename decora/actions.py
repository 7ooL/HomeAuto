from django.core.exceptions import ObjectDoesNotExist
from api_decora.decora_wifi import DecoraWiFiSession
from api_decora.decora_wifi.models.person import Person
from api_decora.decora_wifi.models.residential_account import ResidentialAccount
from api_decora.decora_wifi.models.residence import Residence
from decora.models import Account
import logging

logger = logging.getLogger(__name__)

def turn_on_light(switch):
    if switch.enabled:
        if not switch.power:
            if decora(switch.name, 'ON', 'None'):
                return True
        else:
            logger.debug('switch ' + switch.name + '(' + str(switch.id) + ') is already on')
    else:
        logger.warning('switch ' + switch.name + '(' + str(switch.id) + ') not enabled')
    return False

def turn_off_light(switch):
    if switch.enabled:
        if switch.power:
            if decora(switch.name, 'OFF', 'None'):
                return True
        else:
            logger.debug('switch ' + switch.name + '(' + str(switch.id) + ') is already off')
    else:
        logger.warning('switch ' + switch.name + '(' + str(switch.id) + ') not enabled')
    return False

def decora(switch_name, command, brightness):
    logger.debug('switch:' + switch_name + ' command:' + str(command) + ' brightness: ' + brightness)
    try:
        decoraAcct = Account.objects.get(pk=1)
    except ObjectDoesNotExist as e:
        logger.error(e)
    except:
        logger.error("Error:"+ str(traceback.format_exc()))
    else:
        session = DecoraWiFiSession()
        try:
            session.login(decoraAcct.decora_username, decoraAcct.decora_password)
        except ValueError as err:
            logger.error(str(err).split(',')[0])
        except:
            logger.error("Error:"+ str(traceback.format_exc()))
        else:
            perms = session.user.get_residential_permissions()
            logger.debug('{} premissions'.format(len(perms)))
            all_residences = []
            for permission in perms:
                if permission.residentialAccountId is not None:
                    acct = ResidentialAccount(session, permission.residentialAccountId)
                    for res in acct.get_residences():
                        all_residences.append(res)
                else:
                    if permission.residenceId is not None:
                        res = Residence(session, permission.residenceId)
                        all_residences.append(res)
            for residence in all_residences:
                for switch in residence.get_iot_switches():
                    attribs = {}
                    if switch.name == switch_name:
                        if brightness is not 'None':
                            attribs['brightness'] = brightness
                        if command == 'ON':
                            attribs['power'] = 'ON'
                        else:
                            attribs['power'] = 'OFF'
                        switch.update_attributes(attribs)
                        logger.info(switch.name + ':' + str(attribs)+"-"+str(switch.id) )
            Person.logout(session)
            return True
    return False

