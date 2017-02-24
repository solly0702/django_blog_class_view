from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

from django.contrib import messages

from .forms import UserLoginForm, UserRegisterForm


class LoginView(View):
    template_name = "accounts/account_form.html"
    form_class = UserLoginForm
    title = "Login"

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form, "title": self.title})

    def post(self, request):
        form = self.form_class(request.POST)
        next = request.GET.get("next")
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            login(request, user)
            if next:
                return redirect(next)

        messages.success(request, "Successfully logged in!",
                         extra_tags="alert-success")

        return redirect("posts:index")


class RegisterView(View):
    template_name = "accounts/account_form.html"
    form_class = UserRegisterForm
    title = "Register"

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form, "title": self.title})

    def post(self, request):
        form = self.form_class(request.POST)
        next = request.GET.get("next")
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            user.set_password(password)
            user.save()

            new_user = authenticate(username=user.username, password=user.password)
            login(request, new_user)
            if next:
                return redirect(next)

        messages.success(request, "Successfully registered!",
                         extra_tags="alert-success")

        return redirect("posts:index")


class LogoutView(View):

    def get(self, request):
        logout(request)
        messages.success(request, "Successfully logged out!",
                         extra_tags="alert-success")
        return redirect("posts:index")
