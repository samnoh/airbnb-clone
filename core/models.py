from django.db import models


class AbstractTimeStampModel(models.Model):
    """
    Abstract Time Stamp Model
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
