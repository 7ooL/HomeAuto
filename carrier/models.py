from django.db import models
from django.utils import timezone

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    name = models.CharField(max_length=30)
    enabled = models.BooleanField(default=False)
    def __str__(self):
        return '{}'.format(self.name)
    class Meta:
        ordering = ['name']
        abstract = True

class System(Common):
    ip = models.CharField(max_length=30)
    port = models.IntegerField(default=0)
    mode = models.CharField(max_length=30, blank=True, null=True)

# home, sleep, wake, away, vac, manual
class Profile(models.Model):
    name = models.CharField(max_length=10)
    clsp = models.DecimalField(max_digits=3, decimal_places=1)
    htsp = models.DecimalField(max_digits=3, decimal_places=1)
    fan = models.CharField(max_length=4)
    system = models.ForeignKey(System, on_delete=models.CASCADE, blank=True, null=True)

class Activity(models.Model):
    class Meta:
        verbose_name_plural = 'Activities'
    DAYS = ((0,"Sunday"),(1,"Monday"),(2,"Tuesday"),(3,"Wednesday"),(4,"Thursday"),(5,"Friday"),(6,"Saturday"))
    time = models.TimeField(default=timezone.now)
    activity = models.CharField(max_length=6)
    day = models.IntegerField(choices=DAYS, default=0)
    period = models.IntegerField(default=0)
    enabled = models.BooleanField(default=False)
    system = models.ForeignKey(System, on_delete=models.CASCADE, blank=True, null=True)

class Status(models.Model):
    class Meta:
        verbose_name_plural = 'Statuses'
    rt = models.DecimalField(max_digits=4, decimal_places=1)
    rh = models.DecimalField(max_digits=4, decimal_places=1)
    current_activity = models.CharField(max_length=6)
    htsp = models.DecimalField(max_digits=4, decimal_places=1)
    clsp = models.DecimalField(max_digits=4, decimal_places=1)
    fan = models.CharField(max_length=6)
    hold = models.BooleanField(default=False)
    hold_time = models.TimeField(default=timezone.now, null=True)
    vaca_running = models.BooleanField(default=False)
    heat_mode =  models.CharField(max_length=30)
    temp_unit = models.CharField(max_length=1)
    filtrlvl = models.DecimalField(max_digits=4, decimal_places=1)
    humlvl = models.DecimalField(max_digits=4, decimal_places=1)
    humid = models.BooleanField(default=False)
    system = models.OneToOneField(System, on_delete=models.CASCADE, blank=True, null=True)
