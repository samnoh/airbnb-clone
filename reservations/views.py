import datetime
from django.http import Http404
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from reviews import forms as reivew_forms
from . import models as reservation_models


class CreateError(Exception):
    """ CreateError Definition """

    pass


def create(request, room, year, month, day):
    days = int(request.GET.get("days", 1))
    try:
        date = datetime.datetime(year=year, month=month, day=day)
        room = room_models.Room.objects.get(pk=room)
        reservation_models.BookedDay.objects.get(date=date, reservation__room=room)
        raise CreateError()
    except room_models.Room.DoesNotExist:
        messages.error(request, "Cannot book the room")
        return redirect(reverse("core:home"))
    except reservation_models.BookedDay.DoesNotExist:
        reservation = reservation_models.Reservation.objects.create(
            guest=request.user,
            room=room,
            check_in=date,
            check_out=date + datetime.timedelta(days=days),
        )  # succssefully booked
        return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


class ReservationDetailView(View):
    """ ReservationDetailView Definition """

    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = reservation_models.Reservation.objects.get_or_none(pk=pk)
        if not reservation or (
            reservation.guest != self.request.user
            and reservation.room.host != self.request.user
        ):
            raise Http404()
        form = reivew_forms.CreateReviewForm()
        return render(
            self.request,
            "reservations/reservation_detail.html",
            {"reservation": reservation, "form": form},
        )


def edit_reservation(request, pk, verb):
    reservation = reservation_models.Reservation.objects.get_or_none(pk=pk)
    if not reservation or (
        reservation.guest != request.user and reservation.room.host != request.user
    ):
        raise Http404()
    if verb == "confirm":
        reservation.status = reservation_models.Reservation.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = reservation_models.Reservation.STATUS_CANCELED
        reservation_models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, "Reservation Updated")
    return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))
