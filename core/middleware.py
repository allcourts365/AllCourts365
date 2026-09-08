import re
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Não mexe em superusuários
            if request.user.is_superuser:
                return

            path = request.path
            
            # Rotas permitidas globalmente para manter a sessão
            allowed_patterns = [
                r'^/painel-atleta/',
                r'^/painel-clube/',
                r'^/redirecionar/',
                r'^/api/',
                r'^/accounts/',
                r'^/admin/',
                r'^/login/',
                r'^/logout/',
                r'^/__debug__/',
                r'^/static/',
                r'^/media/',
            ]
            
            is_allowed = any(re.match(pattern, path) for pattern in allowed_patterns)
            
            # Verifica se é um administrador de clubes
            is_admin = request.user.managed_clubs.exists()
            
            if is_admin:
                # Regra do Admin: só desloga se entrar na página de um clube que NÃO gerencia
                match_club = re.match(r'^/clubes/(\d+)/', path)
                if match_club:
                    club_id = int(match_club.group(1))
                    managed_ids = list(request.user.managed_clubs.values_list('id', flat=True))
                    if club_id not in managed_ids:
                        logout(request)
                # Se não for a rota de um clube, não faz nada com o admin
            else:
                # Regra do Atleta: se sair das áreas permitidas (ex: Home, Clubes list), desloga na hora
                # Exceção: vindo do painel de atleta para ver chaves/ranking
                if not is_allowed and request.GET.get('from_dashboard') != '1':
                    logout(request)
