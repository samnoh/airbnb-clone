import requests
from django.conf import settings
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):
    """ LoginView Definition """

    template_name = "users/login.html"
    form_class = forms.LoginForm
    # success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"Welcome, {user.first_name}!")
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect(reverse("core:home"))


class SignUpView(FormView):
    """ SignUpView """

    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    initial = {"first_name": "John", "last_name": "Smith", "email": "123@test.com"}

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # TODO: add success messages
    except models.User.DoesNotExist:
        # TODO: add error messages
        pass
    return redirect(reverse("core:home"))


class GitHubException(Exception):
    pass


def github_login(request):
    client_id = settings.GITHUB_ID
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )


def github_callback(request):
    try:
        client_id = settings.GITHUB_ID
        client_secret = settings.GITHUB_SECRET
        code = request.GET.get("code")
        if code is not None:
            token = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GitHubException("Cannot get access token")
            else:
                access_token = token_json.get("access_token")
                profile = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    if email is None:
                        raise GitHubException("Email should be public")
                    bio = profile_json.get("bio")
                    profile_image = profile_json.get("avatar_url")
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GitHubException(
                                f"Please log in with {user.login_method}"
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                        if profile_image is not None:
                            image = requests.get(profile_image)
                            user.avatar.save(
                                f"{email}-avatar", ContentFile(image.content)
                            )
                    login(request, user)
                    messages.success(request, f"Welcome, {user.first_name}!")
                    return redirect(reverse("core:home"))
                else:
                    raise GitHubException("Cannot get your profile")
        else:
            raise GitHubException("Cannot get authorization code")
    except GitHubException as error:
        messages.error(request, error)
        return redirect(reverse("users:login"))


class KakaoException(Exception):
    pass


def kakao_login(request):
    client_id = settings.KAKAO_ID
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )


def kakao_callback(request):
    try:
        client_id = settings.KAKAO_ID
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        code = request.GET.get("code")
        token = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Cannot get authorization code")
        else:
            token = token_json.get("access_token")
            profile = requests.get(
                "https://kapi.kakao.com/v1/user/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            profile_json = profile.json()
            email = profile_json.get("kaccount_email", None)
            if email is None:
                raise KakaoException("Email should be public")
            else:
                properties = profile_json.get("properties")
                nickname = properties.get("nickname")
                profile_image = properties.get("profile_image")
                try:
                    user = models.User.objects.get(email=email)
                    if user.login_method != models.User.LOGIN_KAKAO:
                        raise KakaoException(f"Please log in with {user.login_method}")
                except models.User.DoesNotExist:
                    user = models.User.objects.create(
                        email=email,
                        username=email,
                        first_name=nickname,
                        login_method=models.User.LOGIN_KAKAO,
                        email_verified=True,
                    )
                    user.set_unusable_password()
                    user.save()
                    if profile_image is not None:
                        image = requests.get(profile_image)
                        user.avatar.save(
                            f"{nickname}-avatar", ContentFile(image.content)
                        )
                login(request, user)
                messages.success(request, f"Welcome, {user.first_name}!")
                return redirect(reverse("core:home"))
    except KakaoException as error:
        messages.error(request, error)
        return redirect(reverse("users:login"))


class UserPofileView(DetailView):
    """ UserPofileView Definition """

    model = models.User
    context_object_name = "user_obj"

    # # override context
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class UpdaetProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    """ UpdaetProfileView Definition """

    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "email",
        "first_name",
        "last_name",
        "gender",
        "bio",
        "language",
        "currency",
    )
    success_message = "Profile updated"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["email"].widget.attrs = {"placeholder": "Email"}
        form.fields["first_name"].widget.attrs = {"placeholder": "First Name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last Name"}
        form.fields["bio"].widget.attrs = {"placeholder": "Bio"}
        return form


class UpdatePasswordView(
    mixins.LoggedInOnlyView,
    mixins.EmailLoginOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):
    """ UpdatePasswordView Definition """

    template_name = "users/update-password.html"
    success_message = "Password updated"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current Password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New Password"}
        form.fields["new_password2"].widget.attrs = {"placeholder": "Confirm Password"}
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()
