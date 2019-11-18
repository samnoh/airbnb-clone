from django.db import models
from . import managers


class AbstractTimeStampModel(models.Model):
    """ Abstract Time Stamp Model """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = managers.CustomReservationManager()

    class Meta:
        abstract = True
