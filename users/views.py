# users/views.py
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView

from .forms import LoginForm, ProfileUpdateForm, RegisterCredentialsForm, RegisterProfileForm
from .models import Profile, User


class RegisterStep1View(View):
    """
    Paso 1: credenciales (crea el usuario con email y password).
    Tras éxito -> login automático y redirige a Paso 2.
    """

    template_name = "users/register_step1.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("users:profile")
        return render(request, self.template_name, {"form": RegisterCredentialsForm()})

    def post(self, request):
        form = RegisterCredentialsForm(request.POST)
        if form.is_valid():
            # Crear usuario
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password"]
            user = User.objects.create_user(email=email, password=password)
            messages.success(request, "Cuenta creada. Ahora completa tu perfil.")
            login(request, user)
            return redirect("users:register_step2")
        return render(request, self.template_name, {"form": form})


class RegisterStep2View(LoginRequiredMixin, View):
    """
    Paso 2: completar perfil. El Profile ya existe por señal post_save.
    """

    template_name = "users/register_step2.html"

    def get(self, request):
        profile = request.user.profile
        form = RegisterProfileForm(instance=profile)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        profile = request.user.profile
        form = RegisterProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil completado correctamente.")
            return redirect("users:profile")
        return render(request, self.template_name, {"form": form})


class LoginView(DjangoLoginView):
    """
    Login usando plantilla propia.
    Nota: Usamos la auth view de Django pero con un formulario custom si prefieres.
    """

    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Si quieres, podrías inyectar info adicional
        return ctx


class LogoutView(DjangoLogoutView):
    """
    Logout y redirección definida en settings.LOGOUT_REDIRECT_URL.
    """

    pass


class ProfileView(LoginRequiredMixin, DetailView):
    """
    Ver el perfil del usuario autenticado.
    """

    model = Profile
    template_name = "users/profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar el perfil del usuario autenticado.
    """

    model = Profile
    form_class = ProfileUpdateForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado.")
        return super().form_valid(form)
