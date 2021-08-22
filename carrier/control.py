from carrier.models import System, Status, Profile, Activity
from homeauto.house import register_hvac_event
from jobs.jobs import build_jobs
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from api_infinitude.pyInfinitude import Infinitude
import logging, time
from pathlib import Path

logger = logging.getLogger(__name__)

ZONE = 0

def start():
    JOBS = (
        ('Carrier', 'Get Carrier Status and Update Database', False, 20, sync_system),
    )
    build_jobs(JOBS)

def connect(system):
    logger.debug('connecting to:' + system.name)
    hvacIP = system.ip
    hvacPort = system.port
    hvacFile = str(Path(__file__).parent.parent.absolute())+'/api_infinitude/' + str(hvacIP) + '_' + str(hvacPort) + '-file.json'
    hvacStatus = str(Path(__file__).parent.parent.absolute())+'/api_infinitude/' + str(hvacIP) + '_' + str(hvacPort) + '-status.json'
    f = open(hvacFile, 'a+')  # open file in append mode
    f.close()
    f = open(hvacStatus, 'a+')  # open file in append mode
    f.close()
    return Infinitude(hvacIP, hvacPort, hvacFile, hvacStatus)


def remove_hold():
    all_system = System.objects.all()
    if all_system.exists():
        for system in all_system:
            if system.enabled:
                hvac = connect(system)
                hvac.pullConfig()
                time.sleep(1)
                hvac.set_zone_hold(ZONE, 'off')
                time.sleep(1)
                hvac.pushConfig()
            else:
                logger.warning(system.name + '  is disabled, will not pull data')

    else:
        logger.warning('There are no system systems configured, this job should be disabled')


def set_temporary_away():
    all_system = System.objects.all()
    if all_system.exists():
        for system in all_system:
            if system.enabled:
                hvac = connect(system)
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
                logger.warning(system.name + '  is disabled, will not pull data')

    else:
        logger.warning('There are no system systems configured, this job should be disabled')


def check_for_status_events(currentStatus, data):
    update = False
    if currentStatus.rt != data['rt']:
        register_hvac_event(currentStatus.system.name, 'relative temperature', currentStatus.rt, data['rt'])
        update = True
    if currentStatus.rh != data['rh']:
        register_hvac_event(currentStatus.system.name, 'relative humidity', currentStatus.rh, data['rh'])
        update = True
    if currentStatus.current_activity != data['current_activity']:
        register_hvac_event(currentStatus.system.name, 'current activity', currentStatus.current_activity, data['current_activity'])
        update = True
    if currentStatus.htsp != data['htsp']:
        register_hvac_event(currentStatus.system.name, 'htsp', currentStatus.htsp, data['htsp'])
        update = True
    if currentStatus.clsp != data['clsp']:
        register_hvac_event(currentStatus.system.name, 'clsp', currentStatus.clsp, data['clsp'])
        update = True
    if currentStatus.fan != data['fan']:
        register_hvac_event(currentStatus.system.name, 'fan', currentStatus.fan, data['fan'])
        update = True
    if currentStatus.hold != data['hold']:
        register_hvac_event(currentStatus.system.name, 'hold', currentStatus.hold, data['hold'])
        update = True
    if currentStatus.hold_time != data['hold_time']:
        register_hvac_event(currentStatus.system.name, 'hold_time', currentStatus.hold_time, data['hold_time'])
        update = True
    if currentStatus.vaca_running != data['vaca_running']:
        register_hvac_event(currentStatus.system.name, 'vaca_running', currentStatus.vaca_running, data['vaca_running'])
        update = True
    if currentStatus.heat_mode != data['heat_mode']:
        register_hvac_event(currentStatus.system.name, 'heat_mode', currentStatus.heat_mode, data['heat_mode'])
        update = True
    if currentStatus.temp_unit != data['temp_unit']:
        register_hvac_event(currentStatus.system.name, 'temp_unit', currentStatus.temp_unit, data['temp_unit'])
        update = True
    if currentStatus.filtrlvl != data['filtrlvl']:
        register_hvac_event(currentStatus.system.name, 'filtrlvl', currentStatus.filtrlvl, data['filtrlvl'])
        update = True
    if currentStatus.humlvl != data['humlvl']:
        register_hvac_event(currentStatus.system.name, 'humlvl', currentStatus.humlvl, data['humlvl'])
        update = True
    if currentStatus.humid != data['humid']:
        register_hvac_event(currentStatus.system.name, 'humid', currentStatus.humid, data['humid'])
        update = True
    return update


def check_for_profile_events(currentProfile, data):
    update = False
    if currentProfile.name != data['name']:
        register_hvac_event(currentProfile.system.name, 'name', currentProfile.name, data['name'])
        update = True
    if currentProfile.clsp != data['clsp']:
        register_hvac_event(currentProfile.system.name, 'clsp', currentProfile.clsp, data['clsp'])
        update = True
    if currentProfile.htsp != data['htsp']:
        register_hvac_event(currentProfile.system.name, 'htsp', currentProfile.htsp, data['htsp'])
        update = True
    if currentProfile.fan != data['fan']:
        register_hvac_event(currentProfile.system.name, 'fan', currentProfile.fan, data['fan'])
        update = True
    return update


def check_for_activity_events(currentActivity, data):
    update = False
    if currentActivity.time != data['time']:
        register_hvac_event(currentActivity.system.name, 'time', currentActivity.time, data['time'])
        update = True
    if currentActivity.activity != data['activity']:
        register_hvac_event(currentActivity.system.name, 'activity', currentActivity.activity, data['activity'])
        update = True
    if currentActivity.day != data['day']:
        register_hvac_event(currentActivity.system.name, 'day', currentActivity.day, data['day'])
        update = True
    if currentActivity.period != data['period']:
        register_hvac_event(currentActivity.system.name, 'period', currentActivity.period, data['period'])
        update = True
    if currentActivity.enabled != data['enabled']:
        register_hvac_event(currentActivity.system.name, 'enabled', currentActivity.enabled, data['enabled'])
        update = True
    return update


def sync_system():
    all_system = System.objects.all()
    if all_system.exists():
        for system in all_system:
            if system.enabled:
                hvac = connect(system)
                if not hvac.pull_status():
                    logger.error('pull_status failed')
                else:
                    data = {}
                    current_mode = System.objects.get(name=(system.name)).mode
                    data['mode'] = hvac.get_current_mode()
                    if current_mode != data['mode']:
                        (System.objects.filter(name=(system.name)).update)(**data)
                        register_hvac_event(system.name, 'mode', current_mode, data['mode'])
                    data = {}
                    data['system'] = system
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
                    if not Status.objects.filter(system=system).exists():
                        logger.info('Creating status for ' + system.name)
                        s = (Status.objects.create)(**data)
                        s.save()
                    else:
                        currentStatus = Status.objects.get(system=system)
                        if check_for_status_events(currentStatus, data):
                            logger.debug('Updating status for ' + system.name)
                            (Status.objects.filter(system=system).update)(**data)
                if not hvac.pull_config():
                    logger.error('pull_config failed')
                else:
                    for day in range(0, 7):
                        for period in range(0, 5):
                            data = {}
                            data['system'] = system
                            data['day'] = day
                            data['period'] = period
                            data['time'] = datetime.strptime(hvac.get_zone_program_day_period_time(ZONE, day, period), '%H:%M').time()
                            data['activity'] = hvac.get_zone_program_day_period_activity(ZONE, day, period)
                            if hvac.get_zone_program_day_period_enabled(ZONE, day, period) == 'on':
                                data['enabled'] = True
                            else:
                                data['enabled'] = False
                            if not Activity.objects.filter(day=day, period=period, system=system).exists():
                                logger.info('Creating ' + data['activity'] + ' for ' + system.name)
                                s = (Activity.objects.create)(**data)
                                s.save()
                            else:
                                currentActivity = Activity.objects.get(day=day, period=period, system=system)
                            if check_for_activity_events(currentActivity, data):
                                logger.debug('Updating ' + data['activity'] + ' for ' + system.name)
                                (Activity.objects.filter(day=day, period=period, system=system).update)(**data)

                    for id in range(0, 5):
                        data = {}
                        data['system'] = system
                        data['name'] = hvac.get_zone_activity_name(ZONE, id)
                        data['fan'] = hvac.get_zone_activity_fan(ZONE, id)
                        data['clsp'] = float(hvac.get_zone_activity_clsp(ZONE, id))
                        data['htsp'] = float(hvac.get_zone_activity_htsp(ZONE, id))
                        if not Profile.objects.filter(system=system, name=(data['name'])).exists():
                            logger.info('Creating ' + data['name'] + ' profile for ' + system.name)
                            s = (Profile.objects.create)(**data)
                            s.save()
                        else:
                            currentProfile = Profile.objects.get(system=system, name=(data['name']))
                            if check_for_profile_events(currentProfile, data):
                                logger.debug('Updating ' + data['name'] + ' profile for ' + system.name)
                                (Profile.objects.filter(system=system, name=(data['name'])).update)(**data)

                    data = {}
                    data['system'] = system
                    data['name'] = 'vacation'
                    data['fan'] = hvac.get_vacfan()
                    data['clsp'] = float(hvac.get_vacmint())
                    data['htsp'] = float(hvac.get_vacmaxt())
                    if not Profile.objects.filter(system=system, name=(data['name'])).exists():
                        logger.info('Creating ' + data['name'] + ' profile for ' + system.name)
                        s = (Profile.objects.create)(**data)
                        s.save()
                    else:
                        currentProfile = Profile.objects.get(system=system, name=(data['name']))
                        if check_for_profile_events(currentProfile, data):
                            logger.debug('Updating ' + data['name'] + ' profile for ' + system.name)
                            (Profile.objects.filter(system=system, name=(data['name'])).update)(**data)
            else:
                logger.warning(system.name + '  is disabled, will not pull data')

    else:
        logger.warning('There are no system systems configured, this job should be disabled')
