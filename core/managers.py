from django.db import models


class CustomReservationManager(models.Manager):
    """ CustomReservationManager Definition """

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
