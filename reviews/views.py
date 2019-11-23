from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from . import forms


def create_review(request, room):
    if request.method == "POST":
        form = forms.CreateReviewForm(request.POST)
        room = room_models.Room.objects.get_or_none(pk=room)
        if not room:
            return redirect(reverse("core:home"))
        if form.is_valid():
            review = form.save()
            review.room = room
            review.user = request.user
            review.save()
            messages.success(request, _("Your review is successfully sumbitted"))
            return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))
