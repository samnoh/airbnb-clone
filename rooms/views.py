from django.utils import timezone
from django.views.generic import ListView
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context
