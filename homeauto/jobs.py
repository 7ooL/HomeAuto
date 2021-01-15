import apscheduler.job, re, os, logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_apscheduler.jobstores import register_events, register_job, DjangoJobStore
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from homeauto.models import Job, HouseMotionDetector, HouseLight, HouseLock, HouseSensor, Trigger, HouseSchedule

from hue.models import Sensor as HueSensor
from hue.models import Light as HueLight
from hue.models import Group as HueGroup
from hue.models import Schedule as HueSchedule
import hue.jobs as HueJobs

from wemo.models import Device as WemoDevice
import wemo.jobs as WemoJobs

from decora.models import Switch as DecoraSwitch
import decora.jobs as DecoraJobs

import vivint.jobs as VivintJobs
from vivint.models import Device

from homeauto.event_logs import log_addition, log_change, log_deletion

import homeauto.house as HouseJobs
import carrier.control as CarrierJobs

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
register_events(scheduler)

def start():
    scheduler.remove_all_jobs()
    scheduler.print_jobs()
    if not scheduler.running:
        scheduler.start()
    for job in Job.objects.all():
        review_job(job)

#@receiver(post_save, sender=Job)
#def receive_job_update(sender, instance, **kwargs):
#    logger.info("Update for "+instance.COMMAND_TYPES[(job.command + 1)][1])
#    review_job(instance)

def review_job(job):
    logger.debug('Reviewing job ' + job.COMMAND_TYPES[(job.command + 1)][1])
    existingJob = scheduler.get_job(job.COMMAND_TYPES[(job.command + 1)][1])
    if existingJob is not None:
        logger.debug('    ' + existingJob.name)
        if job.enabled:
            if existingJob.next_run_time is None:
                logger.debug('Running create job for ' + job.COMMAND_TYPES[(job.command + 1)][1])
                create_job(job)
            else:
                interval_minutes = int(job.interval / 60)
                interval = re.search('interval\\[(.*)\\]', str(existingJob.trigger)).group(1)
                interval = re.split('[:]', interval)
                if job.interval < 60:
                    logger.debug('check interval is < 60: ' + str(job.interval))
                    if int(interval[2]) != int(job.interval):
                        logger.debug(str(interval[2]) + ' != ' + str(job.interval))
                        create_job(job)
                elif interval_minutes <= 60:
                    logger.debug('check interval is <= 60 minutes: ' + str(interval_minutes))
                    if int(interval[1]) != int(interval_minutes):
                        logger.debug(str(interval[1]) + ' != ' + str(interval_minutes))
                        create_job(job)
        elif existingJob.next_run_time is not None:
            try:
                existingJob.pause()
                logger.info('Paused the job for ' + job.COMMAND_TYPES[(job.command + 1)][1])
            except AttributeError as error:
                try:
                    logger.error(error)
                finally:
                    error = None
                    del error

            except Exception as exception:
                try:
                    logger.error(exception, False)
                finally:
                    exception = None
                    del exception

            except:
                logger.debug('No scheduler for job ' + job.COMMAND_TYPES[(job.command + 1)][1])

    else:
        logger.debug('Running create job for ' + job.COMMAND_TYPES[(job.command + 1)][1])
        create_job(job)


def create_job(job):
    if scheduler.get_job(job.COMMAND_TYPES[(job.command + 1)][1]):
        scheduler.reschedule_job((job.COMMAND_TYPES[(job.command + 1)][1]), trigger='interval', seconds=(job.interval))
        existingJob = scheduler.get_job(job.COMMAND_TYPES[(job.command + 1)][1])
        existingJob.resume()
        logger.info('Updating ' + job.COMMAND_TYPES[(job.command + 1)][1] + ' Service')
    elif job.command == 0:
        scheduler.add_job(dropbox_job, 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 1:
        scheduler.add_job((WemoJobs.sync_wemo), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 2:
        scheduler.add_job((DecoraJobs.sync_decora), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 3:
        scheduler.add_job((VivintJobs.sync_vivint_sensors), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 4:
        scheduler.add_job((HueJobs.sync_groups), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 5:
        scheduler.add_job((HueJobs.sync_lights), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 6:
        scheduler.add_job((HueJobs.sync_scenes), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 7:
        scheduler.add_job((HueJobs.sync_sensors), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 8:
        scheduler.add_job((HueJobs.sync_schedules), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 9:
        scheduler.add_job(find_motion_detectors_job, 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 10:
        scheduler.add_job(find_lights_job, 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 11:
        scheduler.add_job((HouseJobs.check_time_triggers), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 12:
        scheduler.add_job(find_locks_job, 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 13:
        scheduler.add_job(find_sensors_job, 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 14:
        scheduler.add_job((CarrierJobs.sync_system), 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    elif job.command == 15:
        scheduler.add_job(find_schedules_job, 'interval', seconds=(job.interval), id=(job.COMMAND_TYPES[(job.command + 1)][1]), max_instances=1, replace_existing=True, coalesce=True)
    else:
        logger.warning('No job has been created for command: ' + job.COMMAND_TYPES[(job.command + 1)][1])


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
    for s in Device.objects.filter(enabled=True, type='wireless_sensor', motion_detector=False):
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
    for s in Device.objects.filter(enabled=True, type='door_lock_device'):
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
    for md in Device.objects.filter(enabled=True, motion_detector=True):
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
