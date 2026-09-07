from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):
    def pre_login(self, request, user, **kwargs):
        # Ignora a verificação de e-mail e faz o login direto se for admin
        if user.pk and (user.is_staff or user.is_superuser or user.managed_clubs.exists()):
            self.login(request, user)
            raise ImmediateHttpResponse(redirect('/admin/'))
        
        # Para usuários normais, continua o fluxo normal do allauth
        return super().pre_login(request, user, **kwargs)
