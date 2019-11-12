from django.http import Http404
from django.views.generic import ListView, DetailView, UpdateView, View
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from users import mixins as user_mixins
from . import models, forms


class HomeView(ListView):
    """
    HomeView Definition
    """

    model = models.Room
    context_object_name = "rooms"
    paginate_by = 8
    paginate_orphans = 1
    ordering = "created"


class RoomDetail(DetailView):
    """
    RoomDetail Definition
    """

    model = models.Room


class SearchView(View):
    """
    SearchView Definition
    """

    def get(self, request):
        country = request.GET.get("country")
        if country:
            form = forms.SearchForm(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}
                if city != "Anywhere":
                    filter_args["city__startswith"] = city
                filter_args["country"] = country
                if room_type is not None:
                    filter_args["room_type"] = room_type
                if price is not None:
                    filter_args["price__lte"] = price
                if guests is not None:
                    filter_args["guests__gte"] = guests
                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms
                if beds is not None:
                    filter_args["beds__gte"] = beds
                if baths is not None:
                    filter_args["baths__gte"] = baths
                if instant_book is True:
                    filter_args["instant_book"] = True
                if superhost is True:
                    filter_args["host__superhost"] = True
                qs = models.Room.objects.filter(**filter_args).order_by("-created")
                if amenities is not None:
                    for amenity in amenities:
                        qs = qs.filter(amenities=amenity)
                if facilities is not None:
                    for facility in facilities:
                        qs = qs.filter(facilities=facility)

                paginator = Paginator(qs, 5, orphans=1)
                page = int(request.GET.get("page", 1))
                rooms = paginator.get_page(page)

                return render(
                    request, "rooms/search.html", {"form": form, "rooms": rooms}
                )
        else:
            form = forms.SearchForm()

        return render(request, "rooms/search.html", {"form": form})


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):
    """ EditRoomView Definition """

    model = models.Room
    template_name = "rooms/room_edit.html"
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:  # if user does not have ownership
            raise Http404()
        return room


class RoomPhotosView(user_mixins.LoggedInOnlyView, RoomDetail):
    """ RoomPhotosView Definition """

    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:  # if user does not have ownership
            raise Http404()
        return room


@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "You can't delete the photo")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo deleted")
        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    """ EditPhotoView """

    model = models.Photo
    template_name = "rooms/photo_edit.html"
    pk_url_kwarg = "photo_pk"
    fields = ("caption",)
    success_message = "Photo updated"

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})
