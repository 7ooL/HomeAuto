from django.conf import settings
from django.utils import timezone
from datetime import datetime


from homeauto.api_infinitude.pyInfinitude import infinitude
from homeauto.models.infinity import Infinity, InfStatus, InfProfile, InfActivity
from homeauto.house import  RegisterHvacEvent

import logging
# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)



def CheckForStatusEvents(currentStatus, data):
    update = False
    if currentStatus.rt != data['rt']:
        RegisterHvacEvent(currentStatus.infinity.name, 'relative temperature', currentStatus.rt, data['rt'] )
        update = True
    if currentStatus.rh != data['rh']:
        RegisterHvacEvent(currentStatus.infinity.name, 'relative humidity', currentStatus.rh, data['rh'] )
        update = True
    if currentStatus.current_activity != data['current_activity']:
        RegisterHvacEvent(currentStatus.infinity.name, 'current activity', currentStatus.current_activity, data['current_activity'] )
        update = True
    if currentStatus.htsp != data['htsp']:
        RegisterHvacEvent(currentStatus.infinity.name, 'htsp', currentStatus.htsp, data['htsp'] )
        update = True
    if currentStatus.clsp != data['clsp']:
        RegisterHvacEvent(currentStatus.infinity.name, 'clsp', currentStatus.clsp, data['clsp'] )
        update = True
    if currentStatus.fan != data['fan']:
        RegisterHvacEvent(currentStatus.infinity.name, 'fan', currentStatus.fan, data['fan'] )
        update = True
    if currentStatus.hold != data['hold']:
        RegisterHvacEvent(currentStatus.infinity.name, 'hold', currentStatus.hold, data['hold'] )
        update = True
    if currentStatus.hold_time != data['hold_time']:
        RegisterHvacEvent(currentStatus.infinity.name, 'hold_time', currentStatus.hold_time, data['hold_time'] )
        update = True
    if currentStatus.vaca_running != data['vaca_running']:
        RegisterHvacEvent(currentStatus.infinity.name, 'vaca_running', currentStatus.vaca_running, data['vaca_running'] )
        update = True
    if currentStatus.heat_mode != data['heat_mode']:
        RegisterHvacEvent(currentStatus.infinity.name, 'heat_mode', currentStatus.heat_mode, data['heat_mode'] )
        update = True
    if currentStatus.temp_unit != data['temp_unit']:
        RegisterHvacEvent(currentStatus.infinity.name, 'temp_unit', currentStatus.temp_unit, data['temp_unit'] )
        update = True
    if currentStatus.filtrlvl != data['filtrlvl']:
        RegisterHvacEvent(currentStatus.infinity.name, 'filtrlvl', currentStatus.filtrlvl, data['filtrlvl'] )
        update = True
    if currentStatus.humlvl != data['humlvl']:
        RegisterHvacEvent(currentStatus.infinity.name, 'humlvl', currentStatus.humlvl, data['humlvl'] )
        update = True
    if currentStatus.humid != data['humid']:
        RegisterHvacEvent(currentStatus.infinity.name, 'humid', currentStatus.humid, data['humid'] )
        update = True
    return update


def CheckForProfileEvents(currentProfile, data):
    update = False
    if currentProfile.name != data['name']:
        RegisterHvacEvent(currentProfile.infinity.name, 'name', currentProfile.name, data['name'])
        update = True
    if currentProfile.clsp != data['clsp']:
        RegisterHvacEvent(currentProfile.infinity.name, 'clsp', currentProfile.clsp, data['clsp'])
        update = True
    if currentProfile.htsp != data['htsp']:
        RegisterHvacEvent(currentProfile.infinity.name, 'htsp', currentProfile.htsp, data['htsp'])
        update = True
    if currentProfile.fan != data['fan']:
        RegisterHvacEvent(currentProfile.infinity.name, 'fan', currentProfile.fan, data['fan'])
        update = True
    return update

def CheckForActivityEvents(currentActivity, data):
    update = False
    if currentActivity.time != data['time']:
        RegisterHvacEvent(currentActivity.infinity.name, 'time', currentActivity.time, data['time'])
        update = True
    if currentActivity.activity != data['activity']:
        RegisterHvacEvent(currentActivity.infinity.name, 'activity', currentActivity.activity, data['activity'])
        update = True
    if currentActivity.day != data['day']:
        RegisterHvacEvent(currentActivity.infinity.name, 'day', currentActivity.day, data['day'])
        update = True
    if currentActivity.period != data['period']:
        RegisterHvacEvent(currentActivity.infinity.name, 'period', currentActivity.period, data['period'])
        update = True
    if currentActivity.enabled != data['enabled']:
        RegisterHvacEvent(currentActivity.infinity.name, 'enabled', currentActivity.enabled, data['enabled'])
        update = True
    return update


def SyncInfinity():
    all_infinity = Infinity.objects.all()
    if all_infinity.exists():
        for infinity in all_infinity:
            if infinity.enabled:
                # in my house we  have two system but both only have the one zone
                zone = 0
                hvacIP = infinity.ip
                hvacPort = infinity.port
                hvacFile = "homeauto/api_infinitude/"+str(hvacIP)+"_"+str(hvacPort)+"-file.json"
                hvacStatus = "homeauto/api_infinitude/"+str(hvacIP)+"_"+str(hvacPort)+"-status.json"
                hvac = infinitude(hvacIP,hvacPort,hvacFile, hvacStatus)

                if not hvac.pullStatus():
                    logger.error("pullStatus failed")
                else:
                    data = {}

                    current_mode = Infinity.objects.get(name=infinity.name).mode
                    # get the HVAC mode
                    data['mode'] = hvac.get_mode();
                    if current_mode != data['mode']:
                        Infinity.objects.filter(name=infinity.name).update(**data)
                        RegisterHvacEvent(infinity.name, 'mode',current_mode,data['mode'])

                    data = {}
                    data['infinity'] = infinity
                    # InfStatus
                    data['rt'] = float(hvac.get_current_zone_rt(zone)) # current temp
                    data['rh'] = float(hvac.get_current_zone_rh(zone)) # current humdiity
                    data['current_activity'] = hvac.get_current_zone_currentActivity(zone)
                    data['htsp'] = float(hvac.get_current_zone_htsp(zone)) # current heat setpoint
                    data['clsp'] = float(hvac.get_current_zone_clsp(zone)) # current cool setpoint

#                    if hvac.get_current_zone_fan(zone) == "on":
#                        data['fan'] = True
#                    else:
#                        data['fan'] = False
                    data['fan'] = hvac.get_current_zone_fan(zone)

                    if hvac.get_current_zone_hold(zone) == "on":
                        data['hold'] = True
                    else:
                        data['hold'] = False
                    hold_time = hvac.get_current_zone_otmr(zone)
                    if hold_time == "[{}]":
                        data['hold_time'] = None
                    else:
                        data['hold_time'] = hold_time


                    if hvac.get_current_vacatrunning() == "on":
                        data['vaca_running'] = True
                    else:
                        data['vaca_running'] = False

                    data['heat_mode'] = hvac.get_current_mode()
                    data['temp_unit'] = hvac.get_current_cfgem() # F or C
                    data['filtrlvl'] = float(hvac.get_current_filtrlvl())
                    data['humlvl'] = float(hvac.get_current_humlvl())

                    if hvac.get_current_humid() == "on":
                        data['humid'] = True
                    else:
                        data['humid'] = False

                    # if the InfStatus doesn't exist, then create it
                    if not InfStatus.objects.filter(infinity=infinity).exists():
                        logger.info("Creating status for "+infinity.name)
                        s = InfStatus.objects.create(**data)
                        s.save()
                    # otherwise update the InfStatus
                    else:
                        currentStatus = InfStatus.objects.get(infinity=infinity)
                        if CheckForStatusEvents(currentStatus, data):
                            logger.debug("Updating status for "+infinity.name)
                            InfStatus.objects.filter(infinity=infinity).update(**data)


                if not hvac.pullConfig():
                    logger.error("pullConfig failed")
                else:
                    # adjust days of week num to align with carrier and infinitude numbering
                    for day in range(0,7):
                          for period in range(0,5):
                              data = {}
                              data['infinity'] = infinity
                              data['day'] = day
                              data['period'] = period
                              data['time'] = datetime.strptime(hvac.get_zone_program_day_period_time(zone, day, period), '%H:%M').time()
                              data['activity'] =  hvac.get_zone_program_day_period_activity(zone, day, period)
                              if hvac.get_zone_program_day_period_enabled(zone, day, period) == "on":
                                  data['enabled'] = True
                              else:
                                  data['enabled'] = False

                              # if the InfActivity doesn't exist, then create it
                              if not InfActivity.objects.filter(day=day, period=period, infinity=infinity).exists():
                                  logger.info("Creating "+data['activity']+" for "+infinity.name)
                                  s = InfActivity.objects.create(**data)
                                  s.save()
                              # otherwise update the InfActivity
                              else:
                                  currentActivity = InfActivity.objects.get(day=day, period=period, infinity=infinity)
                                  if CheckForActivityEvents(currentActivity, data):
                                      logger.debug("Updating "+data['activity']+" for "+infinity.name)
                                      InfActivity.objects.filter(day=day, period=period, infinity=infinity).update(**data)

                    # pull out clsp and htsp for each profile name
                    # id: 0 = home, 1 = away, 2 = sleep, 3 = wake, 4 = manual
                    for id in range(0,5):
                        data = {}
                        data['infinity'] = infinity
                        data['name'] = hvac.get_zone_activity_name(zone, id)
                        data['fan'] = hvac.get_zone_activity_fan(zone, id)
                        data['clsp'] = float(hvac.get_zone_activity_clsp(zone, id))
                        data['htsp'] = float(hvac.get_zone_activity_htsp(zone, id))

                        # if the InfProfile doesn't exist, then create it
                        if not InfProfile.objects.filter(infinity=infinity, name=data['name']).exists():
                            logger.info("Creating "+data['name']+" profile for "+infinity.name)
                            s = InfProfile.objects.create(**data)
                            s.save()
                        # otherwise update the InfProfile
                        else:
                            currentProfile = InfProfile.objects.get(infinity=infinity, name=data['name'])
                            if CheckForProfileEvents(currentProfile,data):
                                logger.debug("Updating "+data['name']+" profile for "+infinity.name)
                                InfProfile.objects.filter(infinity=infinity, name=data['name']).update(**data)

                    # get the vacation data too
                    data = {}
                    data['infinity'] = infinity
                    data['name'] = "vacation"
                    data['fan'] = hvac.get_vacfan()
                    data['clsp'] = float(hvac.get_vacmint())
                    data['htsp'] = float(hvac.get_vacmaxt())

                    # if the InfProfile doesn't exist, then create it
                    if not InfProfile.objects.filter(infinity=infinity, name=data['name']).exists():
                        logger.info("Creating "+data['name']+" profile for "+infinity.name)
                        s = InfProfile.objects.create(**data)
                        s.save()
                    # otherwise update the InfProfile
                    else:
                        currentProfile = InfProfile.objects.get(infinity=infinity, name=data['name'])
                        if CheckForProfileEvents(currentProfile,data):
                            logger.debug("Updating "+data['name']+" profile for "+infinity.name)
                            InfProfile.objects.filter(infinity=infinity, name=data['name']).update(**data)


            else:
                logger.warning(infinity.name+"  is disabled, will not pull data")
    else:
        logger.warning("There are no infinity systems configured, this job should be disabled")
