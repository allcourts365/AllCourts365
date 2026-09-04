from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm, UserProfileForm, PlayerLinkRequestForm
from .models import PlayerLinkRequest
import json
from clubs.models import Club, Player, Match, Court
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

def home(request):
    return render(request, 'home.html')

from django.contrib.auth import logout

@login_required
def login_redirect(request):
    user = request.user
    
    # 1. Se for administrador de algum clube, vai pro Admin do clube
    if user.managed_clubs.exists():
        return render(request, 'admin_redirect.html')
        
    # 2. Atletas, Usuários Novos e SuperAdmins vão pro Dashboard de Atleta
    club_id = request.GET.get('club')
    url = reverse('athlete_dashboard')
    if club_id:
        url += f'?club={club_id}'
    return redirect(url)

@login_required
def athlete_dashboard(request):
    user = request.user
    profile = user.profile
    linked_club = None
    
    # 1. Tentar pegar o clube do jogador vinculado
    if hasattr(user, 'player_profile'):
        linked_club = user.player_profile.club
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserForm(request.POST, instance=user)
            profile_form = UserProfileForm(request.POST, instance=profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('athlete_dashboard')
                
        elif 'link_request' in request.POST:
            link_form = PlayerLinkRequestForm(request.POST)
            if link_form.is_valid():
                req = link_form.save(commit=False)
                req.user = user
                req.save()
                messages.success(request, 'Solicitação enviada! Aguarde a aprovação do clube.')
                return redirect('athlete_dashboard')
                
        elif 'schedule_match' in request.POST:
            match_id = request.POST.get('match_id')
            court_id = request.POST.get('court')
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            
            try:
                match = Match.objects.get(id=match_id)
                court = Court.objects.get(id=court_id)
                
                # Checa se o usuário é realmente um dos jogadores
                if user.player_profile not in [match.player_a, match.player_b]:
                    messages.error(request, 'Você não tem permissão para agendar este jogo.')
                    return redirect('athlete_dashboard')
                    
                # Checa se é a rodada atual
                if match.round_number != match.tournament.current_round:
                    messages.error(request, 'Só é possível agendar jogos da rodada atual.')
                    return redirect('athlete_dashboard')
                    
                dt_str = f"{date_str} {time_str}"
                scheduled_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                scheduled_dt = timezone.make_aware(scheduled_dt)
                
                # Validação de Horário de Expediente
                weekday = scheduled_dt.weekday() # 0 = Monday, 6 = Sunday
                club_obj = match.tournament.club
                t = scheduled_dt.time()
                
                valid_time = False
                if weekday < 5: # Segunda a Sexta
                    if club_obj.weekday_open and club_obj.weekday_close and club_obj.weekday_open <= t <= club_obj.weekday_close:
                        valid_time = True
                elif weekday == 5: # Sábado
                    if club_obj.saturday_open and club_obj.saturday_close and club_obj.saturday_open <= t <= club_obj.saturday_close:
                        valid_time = True
                else: # Domingo
                    if club_obj.sunday_open and club_obj.sunday_close and club_obj.sunday_open <= t <= club_obj.sunday_close:
                        valid_time = True
                        
                if not valid_time:
                    messages.error(request, 'O horário escolhido está fora do expediente do clube para este dia.')
                    return redirect('athlete_dashboard')
                
                # Validação de Conflito de Horário (1h30m = 90 min) na MESMA quadra
                conflict_start = scheduled_dt - timedelta(minutes=89)
                conflict_end = scheduled_dt + timedelta(minutes=89)
                
                conflicts = Match.objects.filter(
                    court=court,
                    scheduled_datetime__range=(conflict_start, conflict_end)
                ).exclude(id=match.id)
                
                if conflicts.exists():
                    messages.error(request, 'A quadra selecionada já possui um jogo marcado próximo a este horário (conflito de 1h30m).')
                else:
                    match.court = court
                    match.scheduled_datetime = scheduled_dt
                    match.save()
                    messages.success(request, 'Jogo marcado com sucesso!')
                    
            except Exception as e:
                messages.error(request, f'Erro ao agendar o jogo: {str(e)}')
            
            return redirect('athlete_dashboard')
    
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
        link_form = PlayerLinkRequestForm()

    # Busca requisições pendentes do usuário
    pending_request = PlayerLinkRequest.objects.filter(user=user, status='pending').first()

    # Prepara dados para o select encadeado (Clube -> Atleta)
    clubs = Club.objects.all().order_by('name')
    players_data = {}
    for c in clubs:
        players_in_club = Player.objects.filter(club=c, user__isnull=True).order_by('name')
        players_data[c.id] = [{'id': p.id, 'name': p.name} for p in players_in_club]

    # Prepara os Jogos do Atleta
    my_matches = []
    courts = []
    if hasattr(user, 'player_profile'):
        p = user.player_profile
        my_matches = Match.objects.filter(Q(player_a=p) | Q(player_b=p)).select_related('tournament', 'player_a', 'player_b', 'court').order_by('-tournament__current_round', 'round_number')
        courts = Court.objects.filter(club=linked_club, is_ranking_court=True)

    context = {
        'linked_club': linked_club,
        'user_form': user_form,
        'profile_form': profile_form,
        'link_form': link_form,
        'pending_request': pending_request,
        'clubs': clubs,
        'players_json': json.dumps(players_data),
        'my_matches': my_matches,
        'courts': courts,
    }
    
    return render(request, 'athlete_dashboard.html', context)
