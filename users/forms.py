# users/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Profile, User


class RegisterCredentialsForm(forms.ModelForm):
    """
    Paso 1 de registro: credenciales.
    - Pedimos email y password + confirmación
    - Validamos password con validadores de Django (fuerza)
    """

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Usa una contraseña robusta.",
    )
    password_confirm = forms.CharField(
        label="Confirma la contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["email"]  # nuestro User no usa username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password")
        pwd2 = cleaned.get("password_confirm")
        if pwd and pwd2 and pwd != pwd2:
            self.add_error("password_confirm", "Las contraseñas no coinciden.")
        # Valida robustez
        if pwd:
            validate_password(pwd)
        return cleaned


class RegisterProfileForm(forms.ModelForm):
    """
    Paso 2 de registro: completar perfil.
    """

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "phone",
            "timezone",
            "avatar",
            "wants_email",
            "wants_sms",
            "wants_push",
        ]


class LoginForm(forms.Form):
    """
    Login por email + contraseña.
    """

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError("Credenciales inválidas.")
        if not user.is_active:
            raise forms.ValidationError("Tu cuenta está inactiva.")
        cleaned["user"] = user
        return cleaned


class ProfileUpdateForm(forms.ModelForm):
    """
    Editar perfil para usuario autenticado.
    """

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "phone",
            "timezone",
            "avatar",
            "wants_email",
            "wants_sms",
            "wants_push",
        ]
