from .models import SiteConfiguration
from clubs.models import Club

def site_config(request):
    try:
        config = SiteConfiguration.load()
    except Exception:
        config = None
        
    club_override = None
    
    # Se estivemos em uma view de detalhe do clube, ele mesmo passa 'club', 
    # mas se for uma view genérica (login) podemos pegar pela URL ?club=
    club_id = request.GET.get('club')
    
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
