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
        fields = [
            'full_name', 'racket', 'handedness', 'backhand',
            'phone', 'birth_date', 'cep', 'address', 'number', 'complement', 'neighborhood', 'city', 'state', 'shirt_size',
            'string_tension', 'string_type', 'play_style', 'best_shot',
            'tennis_idol', 'preferred_time', 'avatar'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

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
                self.fields['player'].queryset = Player.objects.filter(
                    club_id=club_id
                ).exclude(
                    name__icontains='Bye'
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['player'].queryset = self.instance.club.player_set.exclude(
                name__icontains='Bye'
            ).order_by('name')

from allauth.account.forms import SignupForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.utils import timezone

class CustomSignupForm(SignupForm):
    terms_agreement = forms.BooleanField(
        required=True,
        label="Declaro que li e aceito os Termos de Uso e a Política de Privacidade. Caso faça upload de fotos/vídeos de torneios, declaro possuir autorização de imagem dos participantes (e de seus responsáveis, se menores).",
        error_messages={'required': 'Você precisa aceitar os termos para se cadastrar.'}
    )

    captcha = ReCaptchaField(
        label='',
        widget=ReCaptchaV2Checkbox(attrs={
            'data-theme': 'dark'
        })
    )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        
        # Obter IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Atualizar Perfil de Usuário com Auditoria
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.terms_accepted = self.cleaned_data.get('terms_agreement', False)
        profile.terms_version = "v1.0_2024" # Versão atual dos termos
        profile.consent_ip = ip
        profile.consent_date = timezone.now()
        profile.save()
        
        return user
