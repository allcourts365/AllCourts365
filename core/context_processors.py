from .models import SiteConfiguration
from clubs.models import Club
import re

def site_config(request):
    try:
        config = SiteConfiguration.load()
    except Exception:
        config = None
        
    club_override = None
    
    # Pega club_id via query string
    club_id = request.GET.get('club')
    
    # Tenta extrair o ID do clube diretamente de URLs de páginas de clube
    # Ex: /clubes/4/, /ranking/5/ (que tem tournament.club), /eliminatorias/3/
    if not club_id:
        path = request.path
        # Página de detalhe do clube: /clubes/<id>/
        m = re.match(r'^/clubes/(\d+)/', path)
        if m:
            club_id = m.group(1)

    # Usa a sessão para persistir a identidade visual do clube em redirects do allauth e no painel
    if club_id:
        request.session['current_club_id'] = club_id
    elif request.path.startswith('/accounts/') or request.path.startswith('/painel-atleta/') or request.path.startswith('/redirecionar/'):
        club_id = request.session.get('current_club_id')

    if club_id:
        try:
            club_override = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            pass
            
    # Se o club_override existir, podemos retornar ele também
    return {
        'site_config': config,
        'club_context': club_override
    }
