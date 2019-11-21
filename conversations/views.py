from django.shortcuts import render, redirect, reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.db.models import Q
from users import models as user_models
from users import mixins as user_mixins
from . import models, forms


@login_required
def start_conversation(request, host_pk, guest_pk):
    host = user_models.User.objects.get_or_none(pk=host_pk)
    guest = user_models.User.objects.get_or_none(pk=guest_pk)
    if host is not None and guest is not None:
        try:
            conversation = models.Conversation.objects.get(
                Q(participants=host) & Q(participants=guest)
            )
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create()
            conversation.participants.add(host, guest)
        return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(user_mixins.LoggedInOnlyView, View):
    """ ConversationDetailView Definition """

    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        form = forms.AddCommentForm()
        return render(
            self.request,
            "conversations/conversation_detail.html",
            {"conversation": conversation, "form": form},
        )

    def post(self, *args, **kwargs):
        pk = kwargs.get("pk")
        form = forms.AddCommentForm(self.request.POST)
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        if form.is_valid():
            message = form.cleaned_data.get("message")
            models.Message.objects.create(
                message=message, user=self.request.user, conversation=conversation
            )
        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
