from django.db import models

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


class CustomEvent(models.Model):
    name = models.CharField(max_length=60, primary_key=True)
    def __str__(self):
        return '{}'.format(self.name)
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(CustomEvent, self).save(*args, **kwargs)
