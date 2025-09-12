# apps/accounts/views/profile_views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, FormView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from django.conf import settings

from apps.accounts.models import UserProfile

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = [
        "bio", "data_nascimento", "rg", "estado_civil",
        "cargo", "data_admissao",
        "cep", "logradouro", "numero", "complemento", "bairro", "cidade", "uf",
        "notificar_email", "notificar_sistema", "avatar",
    ]
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        # garante que todo user tenha profile; cria se não existir
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("accounts:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        # mantém o usuário logado após trocar a senha
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)
