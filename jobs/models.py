from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Group(models.Model):
    name = models.CharField(max_length=48)
    def __str__(self):
        return '{}'.format(self.name)


class Command(models.Model):
    name = models.CharField(max_length=60)
    group = models.ForeignKey(Group, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return '{}'.format(self.name)

class Job(models.Model):
    command = models.OneToOneField(Command, on_delete=models.CASCADE, blank=True, null=True)
    interval = models.IntegerField(default=600,validators=[MinValueValidator(0),MaxValueValidator(3600)], verbose_name='Run Interval (seconds)' )
    enabled = models.BooleanField(default=False)
