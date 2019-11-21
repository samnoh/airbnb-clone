from django.urls import path
from . import views

app_name = "conversations"

urlpatterns = [
    path("start/<int:host_pk>/<int:guest_pk>/", views.start_conversation, name="start"),
    path("<int:pk>/", views.ConversationDetailView.as_view(), name="detail"),
]
