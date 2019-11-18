import datetime
from django import template
from reservations import models as reservation_models

register = template.Library()


@register.simple_tag
def is_booked(room, date):
    try:
        _date = datetime.datetime(year=date.year, month=date.month, day=date.day)
        reservation_models.BookedDay.objects.get(date=_date, reservation__room=room)
        return True
    except reservation_models.BookedDay.DoesNotExist:
        return False
