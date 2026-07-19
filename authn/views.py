from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core import signing
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import generic

from .emails import check_email_verification_token, send_verification_email
from .forms import CreateAccountForm
from .models import User


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = "profile_detail.html"


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    success_message = "Profile updated successfully."
    model = User
    template_name = "profile_form.html"
    fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "avatar_url",
        "phone_number",
    ]
    success_url = "/user/profile/"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        if "email" in form.changed_data:
            self.object.email_verified = False
            self.object.save(update_fields=["email_verified"])
            send_verification_email(self.object, request=self.request)
        return response


class CreateAccountView(generic.FormView):
    template_name = "registration/create_account.html"
    form_class = CreateAccountForm
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        if user.email:
            send_verification_email(user, request=self.request)
        return super().form_valid(form)


class VerifyEmailView(generic.View):
    def get(self, request, token):
        try:
            user = check_email_verification_token(token)
        except signing.SignatureExpired:
            return HttpResponse("This verification link has expired.", status=400)
        except (signing.BadSignature, User.DoesNotExist):
            return HttpResponse("Invalid verification link.", status=400)

        user.email_verified = True
        user.save(update_fields=["email_verified"])
        messages.success(request, "Your email address has been verified.")
        return redirect("index")
