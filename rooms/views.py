from django.views.generic import ListView, DetailView
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
