from django.db import models
from django.contrib.auth.models import User

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

class SingletonModel(models.Model):

    class Meta:
        abstract = True


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

class Account(models.Model):
    class Meta:
        verbose_name_plural = 'API Account'
    user = models.OneToOneField(User, related_name='vivint_account_created', on_delete=models.CASCADE)
    vivint_username = models.CharField(max_length=60)
    vivint_password = models.CharField(max_length=60)
    pubnub = models.BooleanField(default=False, verbose_name='Subscribe to Realtime Events (requires restart)')
    def save(self, *args, **kwargs):
        self.pk = 1
        super(Account, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

