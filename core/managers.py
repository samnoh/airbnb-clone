from django.db import models
from django.contrib.auth.models import UserManager


class CustomReservationManager(UserManager, models.Manager):
    """ CustomReservationManager Definition """

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
