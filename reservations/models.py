import datetime
from django.db import models
from django.utils import timezone
from core import models as core_models
from users import models as user_models
from rooms import models as room_models


class BookedDay(core_models.AbstractTimeStampModel):
    """ BookedDay Model Definition """

    date = models.DateField()
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"

    def __str__(self):
        return str(self.date)


class Reservation(core_models.AbstractTimeStampModel):
    """ Reservation Model Definition """

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )

    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guest = models.ForeignKey(
        user_models.User, related_name="reservations", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        room_models.Room, related_name="reservations", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.room} - {self.check_in}"

    def in_progress(self):
        now = timezone.now().date()
        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True

    def is_finished(self):
        now = timezone.now().date()
        is_finished = now > self.check_out
        if is_finished:
            BookedDay.objects.filter(reservation=self).delete()
        return is_finished

    is_finished.boolean = True

    def save(self, *args, **kwargs):
        if self.pk is None:
            start = self.check_in
            end = self.check_out
            day_diff = end - start
            if day_diff.days < 1:
                return None
            is_booked = BookedDay.objects.filter(
                date__range=(start, end)
            ).exists()  # return True if it is booked
            if not is_booked:
                super().save(*args, **kwargs)
                for i in range(day_diff.days):
                    date = start + datetime.timedelta(days=i)
                    BookedDay.objects.create(date=date, reservation=self)
        else:
            super().save(*args, **kwargs)
