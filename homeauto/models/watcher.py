from django.db import models

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    name = models.CharField(max_length=30)
    enabled = models.BooleanField(default=False, verbose_name='Usable By HomeAuto')
    class Meta:
        ordering = ['name']
    def __str__(self):
        if self.enabled:
          enabled = "ENABLED"
        else:
          enabled = "DISABLED"
        return '{} - {}'.format(self.name, enabled)
    class Meta:
        abstract = True

class Directory(Common):
    directory = models.CharField(max_length=120)



