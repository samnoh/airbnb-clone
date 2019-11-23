from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.contrib import messages


class LoggedOutOnlyView(UserPassesTestMixin):
    """ LoggedOutOnlyView Definition """

    def test_func(self):
        return not self.request.user.is_authenticated  # True if not logged in

    def handle_no_permission(self):
        messages.error(self.request, _("No permission"))
        return redirect("core:home")


class LoggedInOnlyView(LoginRequiredMixin):
    """ LoggedInOnlyView Definition """

    login_url = reverse_lazy("users:login")


class EmailLoginOnlyView(UserPassesTestMixin):
    """ EmailLoginOnlyView Definition """

    def test_func(self):
        return self.request.user.login_method == "email"

    def handle_no_permission(self):
        messages.error(self.request, _("No permission"))
        return redirect("core:home")
