from django.db import models

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    name = models.CharField(max_length=60)
    enabled = models.BooleanField(default=False, verbose_name='Discoverable By HomeAuto')
    class Meta:
        abstract = True
        ordering = ['name']

class Device(Common):
    type = models.CharField(max_length=30)
    state = models.CharField(max_length=30, blank=True)
    motion_detector = models.BooleanField(default=False)

class Panel(Common):
    id = models.CharField(primary_key=True, max_length=30)
    armed_state = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    zip = models.CharField(max_length=30)



