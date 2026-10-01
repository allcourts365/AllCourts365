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
                r'^/clubes/meus-clubes/',
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

class TermsAcceptanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            # URLs that skip the check
            path = request.path
            exempt_paths = [
                '/aceitar-termos/',
                '/logout/',
                '/logout-redirect/',
                '/termos-de-uso/',
                '/privacidade/',
                '/admin/',
            ]
            
            if any(path.startswith(p) for p in exempt_paths):
                return
                
            if path.startswith('/static/') or path.startswith('/media/'):
                return
                
            # Check if terms are accepted
            if hasattr(request.user, 'profile') and not request.user.profile.terms_accepted:
                return redirect('require_terms_acceptance')

class JazzminThemeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            from django.conf import settings
            from django.core.cache import cache
            from core.models import AdminThemeSetting
            
            theme_config = cache.get('admin_theme_setting')
            
            if theme_config is None:
                # Tenta criar caso não exista
                try:
                    setting = AdminThemeSetting.objects.first()
                    if not setting:
                        setting = AdminThemeSetting.objects.create(theme='darkly', is_dark=True)
                    theme_config = {
                        'theme': setting.theme,
                        'is_dark': setting.is_dark
                    }
                    cache.set('admin_theme_setting', theme_config, 3600)
                except Exception:
                    # Em caso de erro (ex: banco ainda não migrado), fallback
                    theme_config = {'theme': 'darkly', 'is_dark': True}
            
            if hasattr(settings, 'JAZZMIN_UI_TWEAKS'):
                settings.JAZZMIN_UI_TWEAKS['theme'] = theme_config['theme']
                if theme_config['is_dark']:
                    settings.JAZZMIN_UI_TWEAKS['dark_mode_theme'] = theme_config['theme']
                    settings.JAZZMIN_UI_TWEAKS['theme_mode'] = 'dark'
                else:
                    settings.JAZZMIN_UI_TWEAKS['theme_mode'] = 'light'
                    settings.JAZZMIN_UI_TWEAKS.pop('dark_mode_theme', None)
