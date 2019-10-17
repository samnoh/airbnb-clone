from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django_countries import countries
from . import models, forms


class HomeView(ListView):
    """
    HomeView Definition
    """

    model = models.Room
    context_object_name = "rooms"
    paginate_by = 5
    paginate_orphans = 1
    ordering = "created"


class RoomDetail(DetailView):
    """
    RoomDetail Definition
    """

    model = models.Room


def search(request):

    form = forms.SearchForm()
    return render(request, "rooms/search.html", {"form": form})
