from django.conf import settings
from django.utils import timezone
from datetime import datetime
from homeauto.api_infinitude.pyInfinitude import Infinitude
from homeauto.models.infinity import Infinity, InfStatus, InfProfile, InfActivity
from homeauto.house import register_hvac_event
import logging, time

logger = logging.getLogger(__name__)

ZONE = 0

def connect(infinity):
    logger.debug('connecting to:' + infinity.name)
    hvacIP = infinity.ip
    hvacPort = infinity.port
    hvacFile = 'homeauto/api_infinitude/' + str(hvacIP) + '_' + str(hvacPort) + '-file.json'
    hvacStatus = 'homeauto/api_infinitude/' + str(hvacIP) + '_' + str(hvacPort) + '-status.json'
    return Infinitude(hvacIP, hvacPort, hvacFile, hvacStatus)


def remove_hold():
    all_infinity = Infinity.objects.all()
    if all_infinity.exists():
        for infinity in all_infinity:
            if infinity.enabled:
                hvac = connect(infinity)
                hvac.pullConfig()
                time.sleep(1)
                hvac.set_zone_hold(ZONE, 'off')
                time.sleep(1)
                hvac.pushConfig()
            else:
                logger.warning(infinity.name + '  is disabled, will not pull data')

    else:
        logger.warning('There are no infinity systems configured, this job should be disabled')


def set_temporary_away():
    all_infinity = Infinity.objects.all()
    if all_infinity.exists():
        for infinity in all_infinity:
            if infinity.enabled:
                hvac = connect(infinity)
                dt = now + datetime.timedelta(minutes=2)
                newHold = dt.replace(minute=0, second=0) + datetime.timedelta(hours=2, minutes=((dt.minute // 15 + 1) * 15))
                hvac.pullConfig()
                time.sleep(1)
                hvac.set_zone_holdActivity(ZONE, 'away')
                hvac.set_zone_otmr(ZONE, newHold.strftime('%H:%M'))
                hvac.set_zone_hold(ZONE, 'on')
                time.sleep(1)
                logging.info('system(' + str(s) + ') Set AWAY profile until ' + str(newHold))
                hvac.pushConfig()
            else:
                logger.warning(infinity.name + '  is disabled, will not pull data')

    else:
        logger.warning('There are no infinity systems configured, this job should be disabled')


def check_for_status_events(currentStatus, data):
    update = False
    if currentStatus.rt != data['rt']:
        register_hvac_event(currentStatus.infinity.name, 'relative temperature', currentStatus.rt, data['rt'])
        update = True
    if currentStatus.rh != data['rh']:
        register_hvac_event(currentStatus.infinity.name, 'relative humidity', currentStatus.rh, data['rh'])
        update = True
    if currentStatus.current_activity != data['current_activity']:
        register_hvac_event(currentStatus.infinity.name, 'current activity', currentStatus.current_activity, data['current_activity'])
        update = True
    if currentStatus.htsp != data['htsp']:
        register_hvac_event(currentStatus.infinity.name, 'htsp', currentStatus.htsp, data['htsp'])
        update = True
    if currentStatus.clsp != data['clsp']:
        register_hvac_event(currentStatus.infinity.name, 'clsp', currentStatus.clsp, data['clsp'])
        update = True
    if currentStatus.fan != data['fan']:
        register_hvac_event(currentStatus.infinity.name, 'fan', currentStatus.fan, data['fan'])
        update = True
    if currentStatus.hold != data['hold']:
        register_hvac_event(currentStatus.infinity.name, 'hold', currentStatus.hold, data['hold'])
        update = True
    if currentStatus.hold_time != data['hold_time']:
        register_hvac_event(currentStatus.infinity.name, 'hold_time', currentStatus.hold_time, data['hold_time'])
        update = True
    if currentStatus.vaca_running != data['vaca_running']:
        register_hvac_event(currentStatus.infinity.name, 'vaca_running', currentStatus.vaca_running, data['vaca_running'])
        update = True
    if currentStatus.heat_mode != data['heat_mode']:
        register_hvac_event(currentStatus.infinity.name, 'heat_mode', currentStatus.heat_mode, data['heat_mode'])
        update = True
    if currentStatus.temp_unit != data['temp_unit']:
        register_hvac_event(currentStatus.infinity.name, 'temp_unit', currentStatus.temp_unit, data['temp_unit'])
        update = True
    if currentStatus.filtrlvl != data['filtrlvl']:
        register_hvac_event(currentStatus.infinity.name, 'filtrlvl', currentStatus.filtrlvl, data['filtrlvl'])
        update = True
    if currentStatus.humlvl != data['humlvl']:
        register_hvac_event(currentStatus.infinity.name, 'humlvl', currentStatus.humlvl, data['humlvl'])
        update = True
    if currentStatus.humid != data['humid']:
        register_hvac_event(currentStatus.infinity.name, 'humid', currentStatus.humid, data['humid'])
        update = True
    return update


def check_for_profile_events(currentProfile, data):
    update = False
    if currentProfile.name != data['name']:
        register_hvac_event(currentProfile.infinity.name, 'name', currentProfile.name, data['name'])
        update = True
    if currentProfile.clsp != data['clsp']:
        register_hvac_event(currentProfile.infinity.name, 'clsp', currentProfile.clsp, data['clsp'])
        update = True
    if currentProfile.htsp != data['htsp']:
        register_hvac_event(currentProfile.infinity.name, 'htsp', currentProfile.htsp, data['htsp'])
        update = True
    if currentProfile.fan != data['fan']:
        register_hvac_event(currentProfile.infinity.name, 'fan', currentProfile.fan, data['fan'])
        update = True
    return update


def check_for_activity_events(currentActivity, data):
    update = False
    if currentActivity.time != data['time']:
        register_hvac_event(currentActivity.infinity.name, 'time', currentActivity.time, data['time'])
        update = True
    if currentActivity.activity != data['activity']:
        register_hvac_event(currentActivity.infinity.name, 'activity', currentActivity.activity, data['activity'])
        update = True
    if currentActivity.day != data['day']:
        register_hvac_event(currentActivity.infinity.name, 'day', currentActivity.day, data['day'])
        update = True
    if currentActivity.period != data['period']:
        register_hvac_event(currentActivity.infinity.name, 'period', currentActivity.period, data['period'])
        update = True
    if currentActivity.enabled != data['enabled']:
        register_hvac_event(currentActivity.infinity.name, 'enabled', currentActivity.enabled, data['enabled'])
        update = True
    return update


def sync_infinity():
    all_infinity = Infinity.objects.all()
    if all_infinity.exists():
        for infinity in all_infinity:
            if infinity.enabled:
                hvac = connect(infinity)
                if not hvac.pull_status():
                    logger.error('pull_status failed')
                else:
                    data = {}
                    current_mode = Infinity.objects.get(name=(infinity.name)).mode
                    data['mode'] = hvac.get_mode()
                    if current_mode != data['mode']:
                        (Infinity.objects.filter(name=(infinity.name)).update)(**data)
                        register_hvac_event(infinity.name, 'mode', current_mode, data['mode'])
                    data = {}
                    data['infinity'] = infinity
                    data['rt'] = float(hvac.get_current_zone_rt(ZONE))
                    data['rh'] = float(hvac.get_current_zone_rh(ZONE))
                    data['current_activity'] = hvac.get_current_zone_currentActivity(ZONE)
                    data['htsp'] = float(hvac.get_current_zone_htsp(ZONE))
                    data['clsp'] = float(hvac.get_current_zone_clsp(ZONE))
                    data['fan'] = hvac.get_current_zone_fan(ZONE)
                    if hvac.get_current_zone_hold(ZONE) == 'on':
                        data['hold'] = True
                    else:
                        data['hold'] = False
                    hold_time = hvac.get_current_zone_otmr(ZONE)
                    if hold_time == '[{}]':
                        data['hold_time'] = None
                    else:
                        data['hold_time'] = hold_time
                    if hvac.get_current_vacatrunning() == 'on':
                        data['vaca_running'] = True
                    else:
                        data['vaca_running'] = False
                    data['heat_mode'] = hvac.get_current_mode()
                    data['temp_unit'] = hvac.get_current_cfgem()
                    data['filtrlvl'] = float(hvac.get_current_filtrlvl())
                    data['humlvl'] = float(hvac.get_current_humlvl())
                    if hvac.get_current_humid() == 'on':
                        data['humid'] = True
                    else:
                        data['humid'] = False
                    if not InfStatus.objects.filter(infinity=infinity).exists():
                        logger.info('Creating status for ' + infinity.name)
                        s = (InfStatus.objects.create)(**data)
                        s.save()
                    else:
                        currentStatus = InfStatus.objects.get(infinity=infinity)
                        if check_for_status_events(currentStatus, data):
                            logger.debug('Updating status for ' + infinity.name)
                            (InfStatus.objects.filter(infinity=infinity).update)(**data)
                if not hvac.pull_config():
                    logger.error('pull_config failed')
                else:
                    for day in range(0, 7):
                        for period in range(0, 5):
                            data = {}
                            data['infinity'] = infinity
                            data['day'] = day
                            data['period'] = period
                            data['time'] = datetime.strptime(hvac.get_zone_program_day_period_time(ZONE, day, period), '%H:%M').time()
                            data['activity'] = hvac.get_zone_program_day_period_activity(ZONE, day, period)
                            if hvac.get_zone_program_day_period_enabled(ZONE, day, period) == 'on':
                                data['enabled'] = True
                            else:
                                data['enabled'] = False
                            if not InfActivity.objects.filter(day=day, period=period, infinity=infinity).exists():
                                logger.info('Creating ' + data['activity'] + ' for ' + infinity.name)
                                s = (InfActivity.objects.create)(**data)
                                s.save()
                            else:
                                currentActivity = InfActivity.objects.get(day=day, period=period, infinity=infinity)
                            if check_for_activity_events(currentActivity, data):
                                logger.debug('Updating ' + data['activity'] + ' for ' + infinity.name)
                                (InfActivity.objects.filter(day=day, period=period, infinity=infinity).update)(**data)

                    for id in range(0, 5):
                        data = {}
                        data['infinity'] = infinity
                        data['name'] = hvac.get_zone_activity_name(ZONE, id)
                        data['fan'] = hvac.get_zone_activity_fan(ZONE, id)
                        data['clsp'] = float(hvac.get_zone_activity_clsp(ZONE, id))
                        data['htsp'] = float(hvac.get_zone_activity_htsp(ZONE, id))
                        if not InfProfile.objects.filter(infinity=infinity, name=(data['name'])).exists():
                            logger.info('Creating ' + data['name'] + ' profile for ' + infinity.name)
                            s = (InfProfile.objects.create)(**data)
                            s.save()
                        else:
                            currentProfile = InfProfile.objects.get(infinity=infinity, name=(data['name']))
                        if check_for_profile_events(currentProfile, data):
                            logger.debug('Updating ' + data['name'] + ' profile for ' + infinity.name)
                            (InfProfile.objects.filter(infinity=infinity, name=(data['name'])).update)(**data)

                    data = {}
                    data['infinity'] = infinity
                    data['name'] = 'vacation'
                    data['fan'] = hvac.get_vacfan()
                    data['clsp'] = float(hvac.get_vacmint())
                    data['htsp'] = float(hvac.get_vacmaxt())
                    if not InfProfile.objects.filter(infinity=infinity, name=(data['name'])).exists():
                        logger.info('Creating ' + data['name'] + ' profile for ' + infinity.name)
                        s = (InfProfile.objects.create)(**data)
                        s.save()
                    else:
                        currentProfile = InfProfile.objects.get(infinity=infinity, name=(data['name']))
                        if check_for_profile_events(currentProfile, data):
                            logger.debug('Updating ' + data['name'] + ' profile for ' + infinity.name)
                            (InfProfile.objects.filter(infinity=infinity, name=(data['name'])).update)(**data)
            else:
                logger.warning(infinity.name + '  is disabled, will not pull data')

    else:
        logger.warning('There are no infinity systems configured, this job should be disabled')
