from django.conf import settings
from homeauto.models.decora import Switch
from homeauto.models.house import Account
import json, subprocess, logging, sys
from homeauto.api_decora.decora_wifi import DecoraWiFiSession
from homeauto.api_decora.decora_wifi.models.person import Person
from homeauto.api_decora.decora_wifi.models.residential_account import ResidentialAccount
from homeauto.api_decora.decora_wifi.models.residence import Residence
from homeauto.admin_logs import log_addition, log_change, log_deletion
import traceback

logger = logging.getLogger(__name__)

ACCT_NAME = 'Decora'

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
    if Account.objects.filter(name=ACCT_NAME).exists():
        logger.debug('Account name ' + ACCT_NAME + ' exists')
        decoraAcct = Account.objects.get(name=ACCT_NAME)
        if getattr(decoraAcct, 'enabled'):
            logger.debug('Account ' + ACCT_NAME + ' is enabled')
            session = DecoraWiFiSession()
            try:
                session.login(getattr(decoraAcct, 'username'), getattr(decoraAcct, 'password'))
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
            except:
                logger.error("Error:"+ str(traceback.format_exc()))
        else:
            logger.warning('Cannot connect to ' + ACCT_NAME + ' because the account is disabled')
    else:
        logger.error('No account ' + ACCT_NAME + ' exist')
    return False


def sync_decora():
    if Account.objects.filter(name=ACCT_NAME).exists():
        logger.debug('Account name ' + ACCT_NAME + ' exists')
        decoraAcct = Account.objects.get(name=ACCT_NAME)
        if getattr(decoraAcct, 'enabled'):
            logger.debug('Account ' + ACCT_NAME + ' is enabled')
            session = DecoraWiFiSession()
            try:
                session.login(getattr(decoraAcct, 'username'), getattr(decoraAcct, 'password'))
            except:
                logger.error("Error:"+ str(traceback.format_exc()))
            else:
                perms = session.user.get_residential_permissions()
                logger.debug('{} premissions'.format(len(perms)))
                all_residences = []
                for permission in perms:
                    logger.debug('Permission: {}'.format(permission))
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
                        data = {}
                        data['name'] = switch.name
                        data['mic_mute'] = switch.mic_mute
                        data['lang'] = switch.lang
                        data['fadeOnTime'] = switch.fadeOnTime
                        data['serial'] = switch.serial
                        data['configuredAmazon'] = switch.configuredAmazon
                        data['brightness'] = switch.brightness
                        data['downloaded'] = switch.downloaded
                        data['residentialRoomId'] = switch.residentialRoomId
                        data['env'] = switch.env
                        data['timeZoneName'] = switch.timeZoneName
                        data['identify'] = switch.identify
                        data['blink'] = switch.blink
                        data['linkData'] = switch.linkData
                        data['loadType'] = switch.loadType
                        data['isRandomEnabled'] = switch.isRandomEnabled
                        data['ota'] = switch.ota
                        data['otaStatus'] = switch.otaStatus
                        data['connected'] = switch.connected
                        data['allowLocalCommands'] = switch.allowLocalCommands
                        data['long'] = switch.long
                        data['presetLevel'] = switch.presetLevel
                        data['timeZone'] = switch.timeZone
                        data['buttonData'] = switch.buttonData
                        data['id'] = switch.id
                        data['apply_ota'] = switch.apply_ota
                        data['cloud_ota'] = switch.cloud_ota
                        data['canSetLevel'] = switch.canSetLevel
                        data['position'] = switch.position
                        data['customType'] = switch.customType
                        data['autoOffTime'] = switch.autoOffTime
                        data['programData'] = switch.programData
                        data['resKey'] = switch.resKey
                        data['resOcc'] = switch.resOcc
                        data['lat'] = switch.lat
                        data['includeInRoomOnOff'] = switch.includeInRoomOnOff
                        data['model'] = switch.model
                        data['random'] = switch.random
                        data['lastUpdated'] = switch.lastUpdated
                        data['dimLED'] = switch.dimLED
                        data['audio_cue'] = switch.audio_cue
                        data['deleted'] = switch.deleted
                        data['fadeOffTime'] = switch.fadeOffTime
                        data['manufacturer'] = switch.manufacturer
                        data['logging'] = switch.logging
                        data['version'] = switch.version
                        data['maxLevel'] = switch.maxLevel
                        data['statusLED'] = switch.statusLED
                        data['localIP'] = switch.localIP
                        data['rssi'] = switch.rssi
                        data['isAlexaDiscoverable'] = switch.isAlexaDiscoverable
                        data['created'] = switch.created
                        data['mac'] = switch.mac
                        data['dstOffset'] = switch.dstOffset
                        data['dstEnd'] = switch.dstEnd
                        data['residenceId'] = switch.residenceId
                        data['minLevel'] = switch.minLevel
                        data['dstStart'] = switch.dstStart
                        data['onTime'] = switch.onTime
                        data['connectedTimestamp'] = switch.connectedTimestamp
                        if switch.power == 'OFF':
                            data['power'] = False
                        elif switch.power == 'ON':
                            data['power'] = True
                        if not Switch.objects.filter(id=(data['id'])).exists():
                            logger.info('Creating Decora Switch:' + data['name'])
                            s = (Switch.objects.create)(**data)
                            s.save()
                            log_addition(s)
                        else:
                            logger.debug('Updating Decora Switch:' + data['name'])
                            (Switch.objects.filter(id=(data['id'])).update)(**data)

        else:
            logger.warning('Cannot sync Decora data because the account is disabled')
    else:
        logger.error('Cannot sync Decora data because no Account information for ' + ACCT_NAME + '  exist')
