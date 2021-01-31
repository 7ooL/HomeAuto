from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_apscheduler.jobstores import register_events, register_job, DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from jobs.models import Job, Command
from jobs.models import Group as CommandGroup

import logging, time

logger = logging.getLogger(__name__)
SCHEDULER = BackgroundScheduler(settings.SCHEDULER_CONFIG)
register_events(SCHEDULER)

def start():
    if not SCHEDULER.running:
        SCHEDULER.start()

def add_device_group(name):
    logger.debug('name:'+ str(name))
    try:
        g = CommandGroup.objects.get(name=name)
    except ObjectDoesNotExist:
        g = CommandGroup(name=name)
        g.save()
        logger.info("New Command Group Added: "+name)

def add_command(name, group):
    logger.debug('name:'+ str(name))
    logger.debug('group: '+ str(group))
    try:
        c = Command.objects.get(name=name, group=CommandGroup.objects.get(name=group))
    except ObjectDoesNotExist:
        c = Command(name=name, group=CommandGroup.objects.get(name=group))
        c.save()
        logger.info("New Command Added: "+name+" under group: "+group)

def add_job(command, enabled, interval):
    logger.debug('command:'+ str(command))
    logger.debug('enabled:'+ str(enabled))
    logger.debug('interval:'+ str(interval))
    try:
        j = Job.objects.get(command=Command.objects.get(name=command))
    except ObjectDoesNotExist:
        j = Job(command=Command.objects.get(name=command), enabled=enabled, interval=interval)
        j.save()
        logger.info("New Job Added: "+command)
    finally:
        return j

def build_jobs(jobs_list):
    for job in jobs_list:
        add_device_group(job[0])
        add_command(job[1], job[0])
        j = add_job(job[1], job[2], job[3])
        review_job(j,job[4])

@receiver(post_save, sender=Job)
def receive_job_update(sender, instance, **kwargs):
    logger.info("Update for "+str(instance.command))
    update_job(instance)

def update_job(job):
    existingJob = SCHEDULER.get_job(job.command)
    if job.enabled:
        try:
            SCHEDULER.reschedule_job((job.command), trigger='interval', seconds=(job.interval))
            existingJob.resume()
            logger.info('Updating ' + str(job.command) + ' Service, interval='+str(job.interval))
        except:
            SCHEDULER.remove_job(job.command)
            logger.info("Removing old job: "+str(job.command))
    else:
        existingJob.pause()
        logger.info('Paused the job for ' + str(job.command))

def review_job(job, func):
    logger.debug('Reviewing job ' + str(job.command))
    existingJob = SCHEDULER.get_job(job.command)
    if existingJob is not None:
        update_job(job)
    else:
        logger.debug('Running create job for ' + str(job.command))
        create_job(job, func)

def create_job(job, func):
    if SCHEDULER.get_job(job.command):
        SCHEDULER.reschedule_job((job.command), trigger='interval', seconds=(job.interval))
        existingJob = SCHEDULER.get_job(job.command)
        existingJob.resume()
        logger.info('Updating ' + str(job.command) + ' Service')
    else:
        j = SCHEDULER.add_job(func, 'interval', seconds=(job.interval), id=job.command.name, max_instances=1, replace_existing=True, coalesce=True)
        if not job.enabled:
            j.pause()
        logger.warning('Job has been created for command: ' + str(job.command))

#def cleanup_job_executions():
    # remove all job executoions that are more than a week old
#    ts = time.time()

#    for dje in DjangoJobExecution.objects.get(status='Executed', finished=
