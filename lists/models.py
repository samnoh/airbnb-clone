from django.db import models
from core import models as core_models
from users import models as user_models
from rooms import models as room_models


class List(core_models.AbstractTimeStampModel):
    """
    List Model Definition
    """

    name = models.CharField(max_length=80)
    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE)
    rooms = models.ManyToManyField(room_models.Room, blank=True)

    def __str__(self):
        return self.name
