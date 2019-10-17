from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django_countries import countries
from . import models


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


# def room_detail(request, pk):
#     try:
#         room = models.Room.objects.get(pk=pk)
#         return render(request, "rooms/detail.html", {"room": room})
#     except models.Room.DoesNotExist:
#         raise Http404()


def search(request):
    city = str.capitalize(request.GET.get("city", "Anywhere"))
    country = request.GET.get("country", "US")
    room_type = int(request.GET.get("room_type", 0))
    price = int(request.GET.get("price", 0))
    guests = int(request.GET.get("guests", 0))
    bedrooms = int(request.GET.get("bedrooms", 0))
    beds = int(request.GET.get("beds", 0))
    baths = int(request.GET.get("baths", 0))
    instant = request.GET.get('instant', False)
    superhost = request.GET.get('superhost', False)
    selected_amenities = request.GET.getlist("amenities")
    selected_facilities = request.GET.getlist("facilities")
    form = {
        "city": city,
        "selected_country": country,
        "selected_room_type": room_type,
        "price": price,
        "guests": guests,
        "bedrooms": bedrooms,
        "beds": beds,
        "baths": baths,
        "instant": instant,
        "superhost": superhost,
        "selected_amenities": selected_amenities,
        "selected_facilities": selected_facilities,
    }

    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()
    choices = {
        "countries": countries,
        "room_types": room_types,
        "amenities": amenities,
        "facilities": facilities,
    }

    return render(request, "rooms/search.html", {**form, **choices})
