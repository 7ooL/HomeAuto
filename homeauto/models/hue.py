from django.db import models
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    name = models.CharField(max_length=64)
    enabled = models.BooleanField(default=False, verbose_name='Discoverable By HomeAuto')
    def __str__(self):
        if self.enabled:
          enabled = "ENABLED"
        else:
          enabled = "DISABLED"
        return '{} - {}'.format(self.name, enabled)
    class Meta:
        ordering = ['name']
    class Meta:
        abstract = True

class Bridge(Common):
    ip = models.CharField(max_length=15)
    username = models.CharField(max_length=60)
    count_down_lights = models.BooleanField(default=False)
    alarm_use = models.BooleanField(default=False)
    def __str__(self):
        return '{} - {}'.format(self.name, self.ip)


class Schedule(Common):
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE )
    description = models.CharField(max_length=30, default="")
    localtime = models.CharField(max_length=30, default="")
    # status, will use common enabled
    # Hue Application is only allowed to set “enabled” or “disabled”.

# Sensors
class Sensor(Common):
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE, blank=True )
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=30, default="")
    modelid = models.CharField(max_length=15, default="")
    productname = models.CharField(max_length=30, default="", blank=True)
    #state
    lastupdated = models.DateTimeField(blank=True)
      # Hue ambient light sensor
    dark = models.BooleanField(default=False)
    daylight = models.BooleanField(default=False)
    lightlevel = models.IntegerField(default=0, blank=True)
      # Hue temperature sensor
    temperature =  models.IntegerField(default=0, blank=True)
      # Hue motion sensor
    presence = models.BooleanField(default=False)
      #
    #config
    on = models.BooleanField(default=False)
    battery = models.IntegerField(default=0, blank=True)
    reachable = models.BooleanField(default=False)
    alert = models.CharField(max_length=30, default="none", blank=True)
    ledindication = models.BooleanField(default=False)
      # motion sensor
    sensitivity = models.IntegerField(default=0, blank=True)
    sensitivitymax = models.IntegerField(default=0, blank=True)
      # ambient light sensor
    tholddark = models.IntegerField(default=0, blank=True)
    tholdoffset = models.IntegerField(default=0, blank=True)
    motion_detector = models.BooleanField(default=False)

# Lights
class Light(Common):
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE )
    id = models.IntegerField(primary_key=True)
    on = models.BooleanField(default=False)
    hue = models.IntegerField( default=0)
    effect = models.CharField(max_length=30, default="")
    bri = models.IntegerField(default=0)
    sat =  models.IntegerField(default=0)
    ct =  models.IntegerField(default=0)
    xy =  models.CharField(max_length=30, default="")
    alert = models.CharField(max_length=30, default="none")
    colormode = models.CharField(max_length=30, default="")
    reachable = models.BooleanField(default=False)
    type = models.CharField(max_length=30, default="")
    modelid = models.CharField(max_length=15, default="")

# Groups
class Group(Common):
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE )
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=30, default="", null=True,  blank=True)
    lights = models.ManyToManyField(Light)
    on = models.BooleanField(default=False)
    hue = models.IntegerField( default=0)
    effect = models.CharField(max_length=30, default="", null=True,  blank=True)
    bri = models.IntegerField(default=0)
    sat =  models.IntegerField(default=0)
    ct =  models.IntegerField(default=0)
    xy =  models.CharField(max_length=30, default="", null=True,  blank=True)
    alert = models.CharField(max_length=30, default="none", null=True,  blank=True)
    colormode = models.CharField(max_length=30, default="", null=True,  blank=True)
    def __str__(self):
        return '{}'.format(self.name)

class SceneLightstate(models.Model):
    id = models.CharField(primary_key=True, max_length=30)
    bri = models.IntegerField(default=0)
    xy =  models.CharField(max_length=30, default="")
    sat =  models.IntegerField(default=0)
    ct =  models.IntegerField(default=0)
    on = models.BooleanField(default=False)

# Scenes
class Scene(Common):
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE )
    id = models.CharField(primary_key=True, max_length=30)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True,  blank=True)
    lights = models.ManyToManyField(Light)
    type = models.CharField(max_length=30, default="")
    owner = models.CharField(max_length=60, default="")
    lightstates = models.ManyToManyField(SceneLightstate)
    class Meta:
        ordering = ['group']

    def __str__(self):
        return '{} - {}'.format(self.group, self.name)

