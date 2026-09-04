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

from django.contrib.auth.models import User
from .models import UserProfile, PlayerLinkRequest
from clubs.models import Club, Player

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'racket', 'handedness', 'backhand']

class PlayerLinkRequestForm(forms.ModelForm):
    class Meta:
        model = PlayerLinkRequest
        fields = ['club', 'player']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['player'].queryset = Player.objects.none()

        if 'club' in self.data:
            try:
                club_id = int(self.data.get('club'))
                self.fields['player'].queryset = Player.objects.filter(club_id=club_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['player'].queryset = self.instance.club.player_set.order_by('name')
