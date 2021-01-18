from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Job(models.Model):
    COMMAND_TYPES = (
        ('','-------'),
        (0,'Dropbox AutoStart'),
        (1,'Wemo Pull and DB Update'),
        (2,'Decora Pull and DB Update'),
        (3,'Vivint Pull and DB Update'),
        (4,'Hue Groups Pull and DB Update'),
        (5,'Hue Lights Pull and DB Update'),
        (6,'Hue Scenes Pull and DB Update'),
        (7,'Hue Sensors Pull and DB Update'),
        (8,'Hue Schedules Pull and DB Update'),
        (9,'Find House Motion Detectors in Devices'),
        (10,'Find House Lights in Devices'),
        (11,'Evaluate Time Based Triggers'),
        (12,'Find House Locks in Devices'),
        (13,'Find House Sensors in Devices'),
        (14,'Carrier Pull DB Update'),
        (15,'Find House Schedules in Devices'),
    )
    command = models.IntegerField(choices=COMMAND_TYPES, default='')
    interval = models.IntegerField(default=600,validators=[MinValueValidator(0),MaxValueValidator(3600)], verbose_name='Run Interval (seconds)' )
    enabled = models.BooleanField(default=False)


#    def save(self, *args, **kwargs):
#        test = self
#        super(Job, self).save(*args, **kwargs)
#        jobs.create_jobs(test)
#        logger.debug("Running create job for "+self.COMMAND_TYPES[self.command+1][1])
#        if self.enabled:
#            if self.command == 0:
#                try:
#                    jobs.scheduler.add_job(jobs.dropbox_job,'interval', seconds=self.interval, id=self.COMMAND_TYPES[self.command+1][1], max_instances=1, r$
#                except OperationalError as error:
#                    logger.error("job not added")
#            else:
#                logger.warning("No job has been created for command: "+self.COMMAND_TYPES[self.command+1][1])
#        else:
#            logger.debug(self.COMMAND_TYPES[self.command+1][1]+" was not enabled so it was not created")
#        with transaction.atomic():

