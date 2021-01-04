from django.db import models

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Common(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    name = models.CharField(max_length=30)
    enabled = models.BooleanField(default=False, verbose_name='Discoverable By HomeAuto')
    class Meta:
        ordering = ['name']
        abstract = True
    def __str__(self):
        if self.enabled:
          enabled = "ENABLED"
        else:
          enabled = "DISABLED"
        return '{} - {}'.format(self.name, enabled)


class Switch(Common):
    mic_mute = models.CharField(max_length=30, blank=True, null=True)
    lang = models.CharField(max_length=30, blank=True, null=True)
    fadeOnTime = models.IntegerField(default=0)
    serial = models.CharField(max_length=30, blank=True, null=True)
    configuredAmazon = models.CharField(max_length=30, blank=True, null=True)
    brightness = models.IntegerField(default=0)
    downloaded = models.CharField(max_length=30, blank=True, null=True)
    residentialRoomId = models.CharField(max_length=30, blank=True, null=True)
    env = models.IntegerField(default=0)
    timeZoneName = models.CharField(max_length=30, blank=True, null=True)
    identify = models.IntegerField(default=0)
    blink = models.IntegerField(default=0)
    linkData = models.CharField(max_length=30, blank=True, null=True)
    loadType = models.IntegerField(default=0)
    isRandomEnabled = models.BooleanField(default=False)
    ota = models.BooleanField(default=False)
    otaStatus = models.CharField(max_length=30, blank=True, null=True)
    connected = models.BooleanField(default=False)
    allowLocalCommands = models.CharField(max_length=30, blank=True, null=True)
    long = models.CharField(max_length=30, blank=True, null=True)
    presetLevel = models.IntegerField(default=0)
    timeZone = models.IntegerField(default=0)
    buttonData = models.CharField(max_length=30, blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    apply_ota = models.CharField(max_length=30, blank=True, null=True)
    cloud_ota = models.CharField(max_length=30, blank=True, null=True)
    canSetLevel = models.BooleanField(default=False)
    position = models.CharField(max_length=30, blank=True, null=True)
    customType = models.CharField(max_length=30, blank=True, null=True)
    autoOffTime = models.IntegerField(default=0)
    programData = models.CharField(max_length=30, blank=True, null=True)
    resKey = models.CharField(max_length=30, blank=True, null=True)
    resOcc = models.CharField(max_length=30, blank=True, null=True)
    lat = models.CharField(max_length=30, blank=True, null=True)
    includeInRoomOnOff = models.BooleanField(default=False)
    model = models.CharField(max_length=30, blank=True, null=True)
    power = models.BooleanField(default=False, verbose_name='On')
    random = models.BooleanField(default=False)
    lastUpdated = models.CharField(max_length=30, blank=True, null=True)
    dimLED = models.IntegerField(default=0)
    audio_cue = models.CharField(max_length=30, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    fadeOffTime = models.IntegerField(default=0)
    manufacturer = models.CharField(max_length=64, blank=True, null=True)
    logging = models.CharField(max_length=30, blank=True, null=True)
    version = models.CharField(max_length=30, blank=True, null=True)
    maxLevel = models.IntegerField(default=0)
    statusLED = models.IntegerField(default=0)
    localIP = models.CharField(max_length=30, blank=True, null=True)
    rssi = models.CharField(max_length=30, blank=True, null=True)
    isAlexaDiscoverable = models.BooleanField(default=False)
    created = models.CharField(max_length=30, blank=True, null=True)
    mac = models.CharField(max_length=30, blank=True, null=True)
    dstOffset = models.IntegerField(default=0)
    dstEnd = models.IntegerField(default=0)
    residenceId = models.IntegerField(default=0)
    minLevel = models.IntegerField(default=0)
    dstStart = models.IntegerField(default=0)
    onTime = models.IntegerField(default=0)
    connectedTimestamp = models.CharField(max_length=30, blank=True, null=True)


#class Residence(Common):
#    subpremise = models.CharField(max_length=30)
#    energyCost = models.CharField(max_length=30)
#    geopoint_lat = models.CharField(max_length=30)
#    geopoint_lng = models.CharField(max_length=30)
#    transferPending = models.CharField(max_length=30)
#    id = models.IntegerField(primary_key=True)
#    residentialOrganizationId = models.CharField(max_length=30)
#    isRandomEnabled = models.BooleanField(default=False)
#   country = models.CharField(max_length=30)
#    locality = models.CharField(max_length=30)
#    created = models.CharField(max_length=30)
#    status = models.CharField(max_length=30)
#    region = models.CharField(max_length=30)
#    installedByOrganizationId = models.CharField(max_length=30)
#    name = models.CharField(max_length=30)
#    resKey = models.CharField(max_length=30)
#    street = models.CharField(max_length=30)
#    postcode = models.CharField(max_length=30)
#    isOnAwayActivityEnabled = models.BooleanField(default=False)
#    normalize = models.BooleanField(default=False)
#    isOnHomeActivityEnabled = models.BooleanField(default=False)
#    residentialAccountId = models.IntegerField(default=0)
#    lastUpdated = models.CharField(max_length=30)

