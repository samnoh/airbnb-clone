from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView
from rooms import models as room_models
from . import models


def toggle_room(request, room_pk):
    action = request.GET.get("action", None)
    room = room_models.Room.objects.get_or_none(pk=room_pk)
    if room is not None and action is not None:
        _list, created = models.List.objects.get_or_create(
            user=request.user, name="My Favourites Room"
        )
        if action == "add":
            _list.rooms.add(room)
        elif action == "remove":
            _list.rooms.remove(room)
    return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))


class SeeFavsView(TemplateView):
    """ ViewFavsView Definition """

    template_name = "lists/list_detail.html"
