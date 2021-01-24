from homeauto.models import HouseMotionDetector, HouseLight, HouseLock, HouseSensor, Trigger, HouseSchedule
from homeauto.event_logs import log_addition, log_change, log_deletion
from homeauto.house import register_time_event
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from datetime import timedelta
import logging, os, traceback, datetime

from jobs.jobs import build_jobs
from hue.models import Sensor as HueSensor
from hue.models import Light as HueLight
from hue.models import Group as HueGroup
from hue.models import Schedule as HueSchedule
from decora.models import Switch as DecoraSwitch
from vivint.models import Device as VivintDevice
from wemo.models import Device as WemoDevice

logger = logging.getLogger(__name__)

def start():
    JOBS = (
        ('HomeAuto', 'Keep Dropbox Running', False, 900, dropbox_job),
        ('HomeAuto', 'Search Devices for Schedules and Update Database', False, 60, find_schedules_job),
        ('HomeAuto', 'Search Devices for Senosrs and Update Database', False, 60, find_sensors_job),
        ('HomeAuto', 'Search Devices for Locks and Update Database', False, 60, find_locks_job),
        ('HomeAuto', 'Search Devices for Motion Dectors and Update Database', False, 60, find_motion_detectors_job),
        ('HomeAuto', 'Search Devices for Lights and Update Database', False, 60, find_lights_job),
        ('HomeAuto', 'Evaluate Time Bases Trigger', False, 10, check_time_triggers),
    )
    build_jobs(JOBS)


def dropbox_job():
    pidfile = '/home/ha/.dropbox/dropbox.pid'
    command = 'python3 /home/ha/dropbox.py start'
    try:
        with open(pidfile, 'r') as f:
            pid = int(f.read())
        with open('/proc/%d/cmdline' % pid, 'r') as f:
            cmdline = f.read().lower()
    except:
        logger.error('something went wrong trying to read pidfile')
        cmdline = ''

    if cmdline:
        logger.debug('Dropbox is running')
    else:
        logger.warning("Dropbox service isn't running, restarting.")
        os.system(command)


def find_schedules_job():
    for s in HueSchedule.objects.filter(enabled=True):
        try:
            HouseSchedule.objects.get(source_id=(s.id), source=1, source_type=8)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Hue: ' + s.name
            data['source'] = 1
            data['source_type'] = 8
            data['source_id'] = s.id
            x = (HouseSchedule.objects.create)(**data)
            x.save()
            logger.info('Found new schedule: ' + data['name'])
            log_addition(x)

def find_sensors_job():
    for s in VivintDevice.objects.filter(enabled=True, type='wireless_sensor', motion_detector=False):
        try:
            HouseSensor.objects.get(source_id=(s.id), source=0, source_type=5)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Vivint: ' + s.name
            data['source'] = 0
            data['source_type'] = 5
            data['source_id'] = s.id
            x = (HouseSensor.objects.create)(**data)
            x.save()
            logger.info('Found new sensor: ' + data['name'])
            log_addition(x)

def find_locks_job():
    for s in VivintDevice.objects.filter(enabled=True, type='door_lock_device'):
        try:
            HouseLock.objects.get(source_id=(s.id), source=0, source_type=6)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Vivint: ' + s.name
            data['source'] = 0
            data['source_type'] = 6
            data['source_id'] = s.id
            x = (HouseLock.objects.create)(**data)
            x.save()
            logger.info('Found new lock: ' + data['name'])
            log_addition(x)


def find_motion_detectors_job():
    for md in VivintDevice.objects.filter(enabled=True, motion_detector=True):
        try:
            HouseMotionDetector.objects.get(source_id=(md.id), source=0, source_type=7)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Vivint: ' + md.name
            data['source'] = 0
            data['source_type'] = 7
            data['source_id'] = md.id
            x = (HouseMotionDetector.objects.create)(**data)
            x.save()
            logger.info('Found new motion detector: ' + data['name'])
            log_addition(x)

    for md in HueSensor.objects.filter(enabled=True, motion_detector=True):
        try:
            HouseMotionDetector.objects.get(source_id=(md.id), source=1, source_type=7)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Hue: ' + md.name
            data['source'] = 1
            data['source_type'] = 7
            data['source_id'] = md.id
            x = (HouseMotionDetector.objects.create)(**data)
            x.save()
            logger.info('Found new motion detector: ' + data['name'])
            log_addition(x)

def find_lights_job():
    for l in HueLight.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=(l.id), source_type=0)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Hue(light): ' + l.name
            data['source'] = 1
            data['source_type'] = 0
            data['source_id'] = l.id
            x = (HouseLight.objects.create)(**data)
            x.save()
            logger.info('Found new house light: ' + data['name'])
            log_addition(x)

    for l in HueGroup.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=(l.id), source_type=1)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Hue(group): ' + l.name
            data['source'] = 1
            data['source_type'] = 1
            data['source_id'] = l.id
            x = (HouseLight.objects.create)(**data)
            x.save()
            logger.info('Found new house light: ' + data['name'])
            log_addition(x)

    for l in DecoraSwitch.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=(l.id), source_type=3)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Decora(switch): ' + l.name
            data['source'] = 3
            data['source_type'] = 3
            data['source_id'] = l.id
            x = (HouseLight.objects.create)(**data)
            x.save()
            logger.info('Found new house light: ' + data['name'])
            log_addition(x)

    for l in WemoDevice.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=(l.id), source_type=4)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = 'Wemo(plug): ' + l.name
            data['source'] = 2
            data['source_type'] = 4
            data['source_id'] = l.id
            x = (HouseLight.objects.create)(**data)
            x.save()
            logger.info('Found new house light: ' + data['name'])
            log_addition(x)

def check_time_triggers():
    triggers = Trigger.objects.filter(trigger=(Trigger.WINDOW))
    for t in triggers:
        if t.window_start <= timezone.localtime().time() <= t.window_end:
            register_time_event(t)

    triggers = Trigger.objects.filter(trigger=(Trigger.SCHEDULE))
    for t in triggers:
        if t.external_schedule.source == 1:
            try:
                schedule = HueSchedule.objects.get(id=(t.external_schedule.source_id))
            except ObjectDoesNotExist as e:
                logger.error(e)
            except:
                logger.error("Error:"+ str(traceback.format_exc()))
            else:
                time = schedule.localtime
                time_segments = time.split('/T', 1)
                if 'T' in time_segments[0]:
                    start_time = datetime.datetime.strptime(time_segments[0].replace('T', ''), '%H:%M:%S').time()
                    if t.external_schedule_delay > 0:
                        start_time = start_time + timedelta(minutes=t.external_schedule_delay)
                    end_time = datetime.datetime.strptime(time_segments[1], '%H:%M:%S').time()
                    if start_time <= timezone.localtime().time() <= end_time:
                        register_time_event(t)
                elif 'W' in time_segments[0]:
                    day = int(datetime.datetime.today().weekday()) + 1
                    day_mask = int(time_segments[0].replace('W', ''))
                    txt = '{0:08b}'
                    day_list = list(txt.format(day_mask))
                    if int(day_list[day]) == 1:
                        start_time = datetime.datetime.strptime(time_segments[1].replace('T', ''), '%H:%M:%S')
                        if t.external_schedule_delay > 0:
                            start_time = start_time + timedelta(minutes=t.external_schedule_delay)
                        if len(time_segments) > 2:
                            end_time = datetime.datetime.strptime(time_segments[2], '%H:%M:%S').time()
                        else:
                            end_time = (start_time + datetime.timedelta(minutes=1)).time()
                        if start_time.time() <= timezone.localtime().time() <= end_time:
                            register_time_event(t)
                else:
                    logger.error('Hue time format in schedule not accounted for. ' + str(time))
        else:
            logger.warning('There is no external schedule parser setup for type: ' + Trigger.SOURCE[t.external_schedule.source])
