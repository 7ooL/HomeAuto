from decora.models import Switch, Account
from jobs.jobs import build_jobs
from api_decora.decora_wifi import DecoraWiFiSession
from api_decora.decora_wifi.models.person import Person
from api_decora.decora_wifi.models.residential_account import ResidentialAccount
from api_decora.decora_wifi.models.residence import Residence
from django.core.exceptions import ObjectDoesNotExist

import logging, traceback

logger = logging.getLogger(__name__)

def start():
    JOBS = (
        ('Decora', 'Get Decora Device States and Update Database', False, 10, sync_decora),
    )
    build_jobs(JOBS)


def sync_decora():
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
                logger.debug('Permission: {}'.format(permission))
                if permission.residentialAccountId is not None:
                    acct = ResidentialAccount(session, permission.residentialAccountId)
                    for res in acct.get_residences():
                        all_residences.append(res)
                elif permission.residenceId is not None:
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
                        log_addition(decoraAcct, s)
                    else:
                        logger.debug('Updating Decora Switch:' + data['name'])
                        (Switch.objects.filter(id=(data['id'])).update)(**data)


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

