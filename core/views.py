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
            
    # --- Lógica de Lançamento de Resultados e Mensagens ---
        elif 'submit_result' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                # Verifica se o usuário é um dos jogadores e se o jogo está pendente
                if user.player_profile not in [match.player_a, match.player_b] or match.status != 'pending':
                    messages.error(request, 'Não é possível lançar resultado para este jogo.')
                    return redirect('athlete_dashboard')
                
                # Monta o JSON com as parciais propostas
                proposed = {
                    'sets_a': request.POST.get('sets_a'), 'sets_b': request.POST.get('sets_b'),
                    'set1_a': request.POST.get('set1_a'), 'set1_b': request.POST.get('set1_b'),
                    'set2_a': request.POST.get('set2_a'), 'set2_b': request.POST.get('set2_b'),
                    'set3_a': request.POST.get('set3_a'), 'set3_b': request.POST.get('set3_b'),
                    'set4_a': request.POST.get('set4_a'), 'set4_b': request.POST.get('set4_b'),
                    'set5_a': request.POST.get('set5_a'), 'set5_b': request.POST.get('set5_b'),
                }
                
                # Limpa valores vazios e converte pra int
                for k, v in proposed.items():
                    proposed[k] = int(v) if v else None
                    
                match.proposed_result_json = proposed
                match.result_status = 'pending_approval'
                match.reported_by = user.player_profile
                match.save()
                
                # Envia mensagem para o adversário
                opponent = match.player_b if match.player_a == user.player_profile else match.player_a
                if opponent and opponent.user:
                    from core.models import Message
                    Message.objects.create(
                        sender=user,
                        recipient=opponent.user,
                        subject="Novo Resultado Lançado",
                        body=f"{user.player_profile.name} lançou o resultado do jogo {match.tournament.name} (Rodada {match.round_number}). Por favor, acesse seus jogos para aceitar ou rejeitar o placar.",
                        related_match=match
                    )
                
                messages.success(request, 'Resultado lançado! Aguardando aprovação do adversário.')
            except Exception as e:
                messages.error(request, f'Erro ao lançar resultado: {str(e)}')
            return redirect('athlete_dashboard')
            
        elif 'accept_result' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                
                if user.player_profile not in [match.player_a, match.player_b] or match.result_status != 'pending_approval' or match.reported_by == user.player_profile:
                    messages.error(request, 'Você não pode aceitar este resultado.')
                    return redirect('athlete_dashboard')
                
                proposed = match.proposed_result_json or {}
                
                # Transfere os valores do JSON para os campos reais do modelo
                match.sets_a = proposed.get('sets_a')
                match.sets_b = proposed.get('sets_b')
                match.set1_a = proposed.get('set1_a')
                match.set1_b = proposed.get('set1_b')
                match.set2_a = proposed.get('set2_a')
                match.set2_b = proposed.get('set2_b')
                match.set3_a = proposed.get('set3_a')
                match.set3_b = proposed.get('set3_b')
                match.set4_a = proposed.get('set4_a')
                match.set4_b = proposed.get('set4_b')
                match.set5_a = proposed.get('set5_a')
                match.set5_b = proposed.get('set5_b')
                
                match.result_status = 'approved'
                match.save() # Isso vai acionar o cálculo automático de sets e status no models.py
                
                # Mensagem de confirmação pro lançador original
                if match.reported_by and match.reported_by.user:
                    from core.models import Message
                    Message.objects.create(
                        sender=user,
                        recipient=match.reported_by.user,
                        subject="Resultado Aceito",
                        body=f"{user.player_profile.name} aceitou o resultado do jogo {match.tournament.name} (Rodada {match.round_number}). O jogo foi finalizado e os pontos computados.",
                        related_match=match
                    )
                    
                messages.success(request, 'Resultado aceito e jogo finalizado!')
            except Exception as e:
                messages.error(request, f'Erro ao aceitar resultado: {str(e)}')
            return redirect('athlete_dashboard')
            
        elif 'reject_result' in request.POST:
            match_id = request.POST.get('match_id')
            rejection_reason = request.POST.get('rejection_reason', '')[:200]
            try:
                match = Match.objects.get(id=match_id)
                
                if user.player_profile not in [match.player_a, match.player_b] or match.result_status != 'pending_approval' or match.reported_by == user.player_profile:
                    messages.error(request, 'Você não pode rejeitar este resultado.')
                    return redirect('athlete_dashboard')
                
                reported_by_user = match.reported_by.user if match.reported_by else None
                
                match.proposed_result_json = None
                match.result_status = 'unreported'
                match.reported_by = None
                match.save()
                
                # Mensagem de rejeição pro lançador original
                if reported_by_user:
                    from core.models import Message
                    reason_text = f" Motivo: {rejection_reason}" if rejection_reason.strip() else " Nenhum motivo informado."
                    Message.objects.create(
                        sender=user,
                        recipient=reported_by_user,
                        subject="Resultado Rejeitado",
                        body=f"{user.player_profile.name} não aceitou o resultado que você lançou no jogo {match.tournament.name} (Rodada {match.round_number}).{reason_text} Por favor, entre em contato para alinhar o placar correto e lance novamente.",
                        related_match=match
                    )
                    
                messages.success(request, 'Resultado rejeitado. O adversário foi notificado.')
            except Exception as e:
                messages.error(request, f'Erro ao rejeitar resultado: {str(e)}')
            return redirect('athlete_dashboard')
            
        elif 'mark_message_read' in request.POST:
            msg_id = request.POST.get('message_id')
            try:
                from core.models import Message
                msg = Message.objects.get(id=msg_id, recipient=user)
                msg.is_read = True
                msg.save()
            except:
                pass
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

    # Busca Mensagens
    from core.models import Message
    user_messages = Message.objects.filter(recipient=user).order_by('-created_at')
    unread_messages_count = user_messages.filter(is_read=False).count()

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
        'user_messages': user_messages,
        'unread_messages_count': unread_messages_count,
    }
    
    return render(request, 'athlete_dashboard.html', context)

from django.http import JsonResponse

@login_required
def api_court_agenda(request):
    court_id = request.GET.get('court_id')
    date_str = request.GET.get('date')
    
    if not court_id or not date_str:
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)
        
    try:
        court = Court.objects.get(id=court_id)
        club = court.club
        req_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        weekday = req_date.weekday()
        
        # Obter open e close times do clube
        if weekday < 5:
            t_open, t_close = club.weekday_open, club.weekday_close
        elif weekday == 5:
            t_open, t_close = club.saturday_open, club.saturday_close
        else:
            t_open, t_close = club.sunday_open, club.sunday_close
            
        if not t_open or not t_close:
            return JsonResponse({'slots': []}) # Clube fechado neste dia
            
        # Buscar conflitos (jogos agendados nesta quadra neste dia)
        start_of_day = timezone.make_aware(datetime.combine(req_date, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(req_date, datetime.max.time()))
        
        matches = Match.objects.filter(
            court=court,
            scheduled_datetime__range=(start_of_day, end_of_day),
            status__in=['pending', 'completed']
        )
        
        # Gerar slots a cada 30 minutos
        slots = []
        current_time = datetime.combine(req_date, t_open)
        end_time = datetime.combine(req_date, t_close)
        
        while current_time < end_time:
            slot_dt = timezone.make_aware(current_time)
            
            is_booked = False
            conflict_details = None
            
            for m in matches:
                if m.scheduled_datetime:
                    diff = abs((m.scheduled_datetime - slot_dt).total_seconds())
                    if diff < (90 * 60): # 90 minutos de intervalo de segurança
                        is_booked = True
                        conflict_details = f"{m.player_a.name if m.player_a else 'TBD'} vs {m.player_b.name if m.player_b else 'TBD'}"
                        break
                        
            slots.append({
                'time': current_time.strftime('%H:%M'),
                'is_booked': is_booked,
                'details': conflict_details if is_booked else None
            })
            
            current_time += timedelta(minutes=30)
            
        return JsonResponse({'slots': slots})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_monthly_agenda(request):
    court_id = request.GET.get('court_id')
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if not court_id or not year or not month:
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)
        
    try:
        court = Court.objects.get(id=court_id)
        year = int(year)
        month = int(month)
        
        # Calculate start and end of month
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
        start_dt = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        end_dt = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
        
        matches = Match.objects.filter(
            court=court,
            scheduled_datetime__range=(start_dt, end_dt),
            status__in=['pending', 'completed']
        ).select_related('player_a', 'player_b')
        
        # Group by day
        days_data = {}
        for m in matches:
            if not m.scheduled_datetime: continue
            
            day = m.scheduled_datetime.day
            if day not in days_data:
                days_data[day] = []
                
            p1_name = m.player_a.name if m.player_a else "TBD"
            p2_name = m.player_b.name if m.player_b else "TBD"
                
            days_data[day].append({
                'id': m.id,
                'title': f"{p1_name} vs {p2_name}",
                'time': m.scheduled_datetime.strftime('%H:%M')
            })
            
        return JsonResponse({'days': days_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
