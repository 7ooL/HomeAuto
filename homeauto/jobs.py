from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job, DjangoJobStore
import apscheduler.job

import re
from datetime import datetime

from homeauto.models.house import Job, HouseMotionDetector, HouseLight, HouseLock, HouseSensor, Trigger
from homeauto.models.hue import Sensor, Light, Group, Scene
from homeauto.models.wemo import Wemo
from homeauto.models.decora import Switch
from homeauto.models.vivint import Device

import homeauto.hue as HueJobs
import homeauto.vivint as VivintJobs
import homeauto.wemo as WemoJobs
import homeauto.decora as DecoraJobs
import homeauto.house as HouseJobs
import homeauto.infinity as InfinityJobs

import logging
# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
register_events(scheduler)

def start():
    scheduler.remove_all_jobs()
    scheduler.print_jobs()
    if not scheduler.running:
        scheduler.start()

    for job in Job.objects.all():
        review_job(job)

def review_job(job):
    logger.debug("Running create job for "+job.COMMAND_TYPES[job.command+1][1])
    existingJob = scheduler.get_job(job.COMMAND_TYPES[job.command+1][1])
    if existingJob is not None:
        if job.enabled:
            if existingJob.next_run_time is None:
                create_job(job)
            else:
                interval_minutes = int(job.interval/60)
                interval = re.search('interval\[(.*)\]', str(existingJob.trigger)).group(1)
                interval = re.split('[:]',interval)

                # if the interval has changed
                if job.interval < 60:
                    logger.debug("check interval is < 60: "+str(job.interval))
                    if int(interval[2]) != int(job.interval) :
                        logger.debug(str(interval[2])+" != "+str(job.interval))
                        create_job(job)
                # minutes
                elif interval_minutes <= 60:
                    logger.debug("check interval is <= 60 minutes: "+str(interval_minutes))
                    if int(interval[1]) != int(interval_minutes) :
                        logger.debug(str(interval[1])+" != "+str(interval_minutes))
                        create_job(job)

        else:
            if existingJob.next_run_time is not None:
                try:
                    existingJob.pause()
                    logger.info("Paused the job for "+job.COMMAND_TYPES[job.command+1][1])
                except AttributeError as error:
                    logger.error(error)
                except Exception as exception:
                    logger.error(exception, False)
                except:
                    logger.debug("No scheduler for job "+job.COMMAND_TYPES[job.command+1][1])
    else:
        create_job(job)


def create_job(job):
    if scheduler.get_job(job.COMMAND_TYPES[job.command+1][1]):
        scheduler.reschedule_job(job.COMMAND_TYPES[job.command+1][1],trigger='interval',seconds=job.interval)
        existingJob = scheduler.get_job(job.COMMAND_TYPES[job.command+1][1])
        existingJob.resume()
        logger.info("Updating "+job.COMMAND_TYPES[job.command+1][1]+" Service")
    else:
        if job.command == 0:
            scheduler.add_job(dropbox_job,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 1:
            scheduler.add_job(WemoJobs.sync_wemo,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 2:
            scheduler.add_job(DecoraJobs.sync_decora,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 3:
            scheduler.add_job(VivintJobs.sync_vivint_sensors,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 4:
            scheduler.add_job(HueJobs.sync_groups,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 5:
            scheduler.add_job(HueJobs.sync_lights,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 6:
            scheduler.add_job(HueJobs.sync_scenes,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 7:
            scheduler.add_job(HueJobs.sync_sensors,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 8:
            scheduler.add_job(HueJobs.sync_schedules,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 9:
            scheduler.add_job(find_motion_detectors_job,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 10:
            scheduler.add_job(find_lights_job,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 11:
            scheduler.add_job(HouseJobs.check_trigger_windows,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 12:
            scheduler.add_job(find_locks_job,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 13:
            scheduler.add_job(find_sensors_job,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        elif job.command == 14:
            scheduler.add_job(InfinityJobs.sync_infinity,'interval', seconds=job.interval, id=job.COMMAND_TYPES[job.command+1][1], max_instances=1, replace_existing=True, coalesce=True)
        else:
            logger.warning("No job has been created for command: "+job.COMMAND_TYPES[job.command+1][1])

def dropbox_job():
    pidfile = '/home/ha/.dropbox/dropbox.pid'
    command = 'python3 /home/ha/dropbox.py start'
    try:
        with open(pidfile, "r") as f:
            pid = int(f.read())
        with open("/proc/%d/cmdline" % pid, "r") as f:
            cmdline = f.read().lower()
    except:
        logger.error("something went wrong trying to read pidfile")
        cmdline = ""
    if cmdline:
        logger.debug("Service: "+name+" is running")
    else:
        logger.warning("Service: "+name+" isn't running")
        os.system(command)

def find_sensors_job():
    for s in Device.objects.filter(enabled=True, type='wireless_sensor', motion_detector=False):
        try:
            HouseSensor.objects.get(source_id=s.id, source=0, source_type=5)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Vivint: "+s.name
            data['source'] = 0
            data['source_type'] = 5
            data['source_id'] = s.id
            x = HouseSensor.objects.create(**data)
            x.save()
            logger.info("Found new sensor: "+data['name'])

def find_locks_job():
    for s in Device.objects.filter(enabled=True, type='door_lock_device'):
        try:
            HouseLock.objects.get(source_id=s.id, source=0, source_type=6)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Vivint: "+s.name
            data['source'] = 0
            data['source_type'] = 6
            data['source_id'] = s.id
            x = HouseLock.objects.create(**data)
            x.save()
            logger.info("Found new lock: "+data['name'])

def find_motion_detectors_job():
    for md in Device.objects.filter(enabled=True, motion_detector=True):
        try:
            HouseMotionDetector.objects.get(source_id=md.id, source=0, source_type=7)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Vivint: "+md.name
            data['source'] = 0
            data['source_type'] = 7
            data['source_id'] = md.id
            x = HouseMotionDetector.objects.create(**data)
            x.save()
            logger.info("Found new motion detector: "+data['name'])
    for md in Sensor.objects.filter(enabled=True, motion_detector=True):
        try:
            HouseMotionDetector.objects.get(source_id=md.id, source=1, source_type=7)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Hue: "+md.name
            data['source'] = 1
            data['source_type'] = 7
            data['source_id'] = md.id
            x = HouseMotionDetector.objects.create(**data)
            x.save()
            logger.info("Found new motion detector: "+data['name'])

def find_lights_job():
    for l in Light.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=l.id,source_type=0)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Hue(light): "+l.name
            data['source'] = 1
            data['source_type'] = 0
            data['source_id'] = l.id
            x = HouseLight.objects.create(**data)
            x.save()
            logger.info("Found new house light: "+data['name'])
    for l in Group.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=l.id,source_type=1)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Hue(group): "+l.name
            data['source'] = 1
            data['source_type'] = 1
            data['source_id'] = l.id
            x = HouseLight.objects.create(**data)
            x.save()
            logger.info("Found new house light: "+data['name'])
    for l in Switch.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=l.id,source_type=3)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Decora(switch): "+l.name
            data['source'] = 3
            data['source_type'] = 3
            data['source_id'] = l.id
            x = HouseLight.objects.create(**data)
            x.save()
            logger.info("Found new house light: "+data['name'])
    for l in Wemo.objects.filter(enabled=True):
        try:
            HouseLight.objects.get(source_id=l.id,source_type=4)
        except ObjectDoesNotExist:
            data = {}
            data['name'] = "Wemo(plug): "+l.name
            data['source'] = 2
            data['source_type'] = 4
            data['source_id'] = l.id
            x = HouseLight.objects.create(**data)
            x.save()
            logger.info("Found new house light: "+data['name'])

