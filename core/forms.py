from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_superuser:
            raise ValidationError(
                "Administradores do AllCourts365 devem fazer login pelo botão 'Admin AllCourts365' na página inicial.",
                code='invalid_login'
            )
