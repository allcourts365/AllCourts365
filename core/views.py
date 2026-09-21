from django.shortcuts import render, redirect, get_object_or_404
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
from django.shortcuts import redirect

def logout_and_redirect(request):
    next_url = request.GET.get('next', '/')
    logout(request)
    return redirect(next_url)

@login_required
def login_redirect(request):
    user = request.user
    
    # 1. Se for membro da equipe ou superuser, vai para o painel admin do django
    if user.is_staff or user.is_superuser:
        return redirect('/admin/')
    
    # 2. Se for administrador de algum clube, vai pro Admin do clube
    if user.managed_clubs.exists():
        return render(request, 'admin_redirect.html')
        
    # 2.5 Se o usuário tiver inscrição 'pending_waitlist', forçar ida pro pagamento (Step 3)
    from clubs.models import CategoryPlayer
    pending_cp = CategoryPlayer.objects.filter(player__user=user, payment_status='pending_waitlist').first()
    if pending_cp:
        return redirect('clubs:registration_resume', club_id=pending_cp.category.tournament.club.id, tournament_id=pending_cp.category.tournament.id, cp_id=pending_cp.id)
        
    # 3. Atletas, Usuários Novos vão pro Dashboard de Atleta
    club_id = request.GET.get('club')
    url = reverse('athlete_dashboard')
    if club_id:
        url += f'?club={club_id}'
    return redirect(url)

@login_required
def athlete_dashboard(request):
    user = request.user
    profile = user.profile
    
    # 1. Determinar o Clube Ativo e o Perfil de Atleta (Player) correspondente
    club_id_str = request.GET.get('club') or request.POST.get('active_club_id') or request.session.get('active_club_id')
    
    if not club_id_str:
        first_profile = user.player_profiles.first()
        if first_profile:
            club_id_str = str(first_profile.club_id)
        else:
            club_id_str = 'all'
        
    club_id = None
    if club_id_str and club_id_str != 'all':
        try:
            club_id = int(club_id_str)
        except ValueError:
            pass
            
    my_profiles = user.player_profiles.all()
    active_profile = None
    linked_club = None
    
    if club_id:
        active_profile = my_profiles.filter(club_id=club_id).first()
        if not active_profile:
            try:
                linked_club = Club.objects.get(id=club_id)
            except Club.DoesNotExist:
                pass
                
    # Para a aba Meu Perfil, definimos um default player_profile se houver, 
    # mesmo que a visão seja global, para poder atualizar dados do usuário.
    default_profile = my_profiles.first()
    
    print(f'DEBUG: club_id_str={club_id_str}, club_id={club_id}, active_profile={active_profile}, linked_club={linked_club}')
    if club_id_str == 'all':
        request.session['active_club_id'] = 'all'
        request.session['current_club_id'] = 'all'
        # linked_club e active_profile permanecem None na visão global
    elif active_profile:
        linked_club = active_profile.club
        request.session['active_club_id'] = str(linked_club.id)
        request.session['current_club_id'] = str(linked_club.id)
    elif linked_club:
        request.session['active_club_id'] = str(linked_club.id)
        request.session['current_club_id'] = str(linked_club.id)
        
    user_form = UserForm(instance=user)
    profile_form = UserProfileForm(instance=profile)
    link_form = PlayerLinkRequestForm()
    
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
                
                # Verifica se já existe uma solicitação pendente ou se já está vinculado
                if PlayerLinkRequest.objects.filter(user=user, club=req.club, status='pending').exists():
                    messages.warning(request, 'Você já tem uma solicitação de vínculo em análise para este clube!')
                elif Player.objects.filter(user=user, club=req.club).exists():
                    messages.warning(request, 'Você já possui um vínculo com este clube!')
                else:
                    req.save()
                    messages.success(request, 'Solicitação enviada! Aguarde a aprovação do clube.')
                return redirect('athlete_dashboard')
        elif 'resubmit_link_request' in request.POST:
            req_id = request.POST.get('request_id')
            try:
                req = PlayerLinkRequest.objects.get(id=req_id, user=user)
                if req.status == 'rejected':
                    req.status = 'pending'
                    req.save()
                    messages.success(request, 'Solicitação enviada novamente! Aguarde a aprovação do clube.')
            except PlayerLinkRequest.DoesNotExist:
                messages.error(request, 'Solicitação não encontrada.')
            return redirect('athlete_dashboard')
                
        elif 'schedule_match' in request.POST:
            match_id = request.POST.get('match_id')
            court_id = request.POST.get('court')
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            
            try:
                match = Match.objects.get(id=match_id)
                active_profile = match.player_a if match.player_a and match.player_a.user == user else (match.player_b if match.player_b and match.player_b.user == user else active_profile)
                
                # Marcar mensagens relacionadas como lidas
                from core.models import Message
                Message.objects.filter(related_match=match, recipient=user, is_read=False).update(is_read=True)
                
                court = Court.objects.get(id=court_id)
                
                # Checa se o usuário é realmente um dos jogadores
                if active_profile not in [match.player_a, match.player_b]:
                    messages.error(request, 'Você não tem permissão para agendar este jogo.')
                    return redirect('athlete_dashboard')
                    
                # Checa se é a rodada atual
                if match.round_number != match.tournament.current_round:
                    messages.error(request, 'Só é possível agendar jogos da rodada atual.')
                    return redirect('athlete_dashboard')
                    
                dt_str = f"{date_str} {time_str}"
                scheduled_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                scheduled_dt = timezone.make_aware(scheduled_dt)
                
                # Validação de Horário no Passado
                if scheduled_dt < timezone.now():
                    messages.error(request, 'Não é possível agendar um jogo em um horário no passado.')
                    return redirect('athlete_dashboard')
                
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
                    # Se já havia um agendamento/proposta anterior, registra que é um reagendamento
                    is_reschedule = match.schedule_status in ['agendado', 'aguardando_adversario']
                    old_datetime = match.scheduled_datetime
                    
                    # Deleta mensagens antigas de agendamento/reagendamento pendentes
                    from core.models import Message
                    Message.objects.filter(related_match=match, subject__in=["Proposta de Agendamento", "Reagendamento Proposto"]).delete()
                    
                    # Limpa o agendamento anterior
                    match.scheduled_datetime = None
                    match.court = None
                    
                    # Salva nova proposta
                    match.proposed_court = court
                    match.proposed_datetime = scheduled_dt
                    match.schedule_status = 'aguardando_adversario'
                    match.proposed_by = active_profile
                    match.save()
                    
                    # Notify opponent
                    opponent = match.player_b if match.player_a == active_profile else match.player_a
                    if opponent and opponent.user:
                        from core.models import Message
                        if is_reschedule:
                            subject = "Reagendamento Proposto"
                            body = f"{active_profile.name} está propondo um REAGENDAMENTO do jogo {match.tournament.name} do {match.tournament.club.name} (Rodada {match.round_number}). Nova proposta: {scheduled_dt.strftime('%d/%m/%Y às %H:%M')} na {court.name}. O agendamento anterior foi cancelado. Vá para o novo agendamento clicando no botão abaixo."
                        else:
                            subject = "Proposta de Agendamento"
                            body = f"{active_profile.name} propôs agendar o jogo {match.tournament.name} do {match.tournament.club.name} (Rodada {match.round_number}) para o dia {scheduled_dt.strftime('%d/%m/%Y às %H:%M')} na {court.name}. Vá para o novo agendamento clicando no botão abaixo."
                        Message.objects.create(
                            sender=user,
                            recipient=opponent.user,
                            subject=subject,
                            body=body,
                            related_match=match
                        )
                    
                    if is_reschedule:
                        messages.success(request, 'Reagendamento proposto! O adversário foi notificado para confirmar.')
                    else:
                        messages.success(request, 'Proposta de agendamento enviada com sucesso ao seu adversário!')
                    
            except Exception as e:
                messages.error(request, f'Erro ao agendar o jogo: {str(e)}')
            return redirect(reverse('athlete_dashboard') + '?tab=mensagens')
            
        elif 'accept_schedule' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                active_profile = match.player_a if match.player_a and match.player_a.user == user else (match.player_b if match.player_b and match.player_b.user == user else active_profile)
                
                # Marcar mensagens relacionadas como lidas
                from core.models import Message
                Message.objects.filter(related_match=match, recipient=user, is_read=False).update(is_read=True)
                
                # Verifica se a pessoa logada é realmente do jogo
                if active_profile not in [match.player_a, match.player_b]:
                    messages.error(request, 'Permissão negada.')
                    return redirect('athlete_dashboard')
                    
                if match.schedule_status != 'aguardando_adversario':
                    messages.error(request, 'Não há proposta pendente para este jogo.')
                    return redirect('athlete_dashboard')
                    
                # Checa conflitos de novo antes de cravar
                conflict_start = match.proposed_datetime - timedelta(minutes=89)
                conflict_end = match.proposed_datetime + timedelta(minutes=89)
                
                conflicts = Match.objects.filter(
                    court=match.proposed_court,
                    scheduled_datetime__range=(conflict_start, conflict_end)
                ).exclude(id=match.id)
                
                if conflicts.exists():
                    messages.error(request, 'A quadra não está mais disponível neste horário. Por favor, recuse e proponha um novo horário.')
                else:
                    match.scheduled_datetime = match.proposed_datetime
                    match.court = match.proposed_court
                    match.schedule_status = 'agendado'
                    match.save()
                    
                    if match.proposed_by and match.proposed_by.user:
                        from core.models import Message
                        local_dt = timezone.localtime(match.scheduled_datetime)
                        Message.objects.create(
                            sender=user,
                            recipient=match.proposed_by.user,
                            subject="Agendamento Aceito!",
                            body=f"{active_profile.name} aceitou sua proposta! O jogo {match.tournament.name} do {match.tournament.club.name} foi marcado para {local_dt.strftime('%d/%m/%Y às %H:%M')} na {match.court.name}.",
                            related_match=match
                        )
                    messages.success(request, 'Agendamento confirmado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro: {str(e)}')
            return redirect(reverse('athlete_dashboard') + '?tab=mensagens')
                
        elif 'decline_schedule' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                active_profile = match.player_a if match.player_a and match.player_a.user == user else (match.player_b if match.player_b and match.player_b.user == user else active_profile)
                # Marcar mensagens relacionadas como lidas
                from core.models import Message
                Message.objects.filter(related_match=match, recipient=user, is_read=False).update(is_read=True)
                
                if active_profile not in [match.player_a, match.player_b]:
                    messages.error(request, 'Permissão negada.')
                    return redirect('athlete_dashboard')
                    
                proposer = match.proposed_by
                
                match.schedule_status = 'unagendado'
                match.proposed_datetime = None
                match.proposed_court = None
                match.proposed_by = None
                match.save()
                
                if proposer and proposer.user:
                    from core.models import Message
                    Message.objects.create(
                        sender=user,
                        recipient=proposer.user,
                        subject="Proposta Recusada - Aguardando Contraproposta",
                        body=f"{active_profile.name} recusou sua proposta de agendamento do jogo {match.tournament.name} do {match.tournament.club.name} e vai sugerir um novo horário.",
                        related_match=match
                    )
                messages.success(request, 'Proposta recusada. A agenda está aberta para você sugerir um novo horário!')
            except Exception as e:
                messages.error(request, f'Erro: {str(e)}')
                return redirect('athlete_dashboard')
            # Redireciona para o novo calendário para fazer a contraproposta
            return redirect('athlete_calendar')
                
        elif 'delete_schedule' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                active_profile = match.player_a if match.player_a and match.player_a.user == user else (match.player_b if match.player_b and match.player_b.user == user else active_profile)
                
                # Marcar mensagens relacionadas como lidas
                from core.models import Message
                Message.objects.filter(related_match=match, recipient=user, is_read=False).update(is_read=True)
                
                if active_profile not in [match.player_a, match.player_b]:
                    messages.error(request, 'Permissão negada.')
                    return redirect('athlete_dashboard')
                
                # Avisar o outro jogador que o agendamento foi apagado
                opponent = match.player_b if match.player_a == active_profile else match.player_a
                if opponent and opponent.user and (match.schedule_status == 'agendado' or match.schedule_status == 'aguardando_adversario'):
                    from core.models import Message
                    Message.objects.create(
                        sender=user,
                        recipient=opponent.user,
                        subject="Agendamento Cancelado",
                        body=f"{active_profile.name} excluiu o agendamento atual do jogo {match.tournament.name} do {match.tournament.club.name}. Vocês precisam combinar e marcar um novo horário.",
                        related_match=match
                    )
                    
                match.schedule_status = 'unagendado'
                match.scheduled_datetime = None
                match.court = None
                match.proposed_datetime = None
                match.proposed_court = None
                match.proposed_by = None
                match.save()
                
                messages.success(request, 'Agendamento excluído com sucesso. Você já pode remarcar o jogo.')
            except Exception as e:
                messages.error(request, f'Erro: {str(e)}')
            return redirect(reverse('athlete_dashboard') + '?tab=mensagens')

        # --- Lógica de Lançamento de Resultados e Mensagens ---
        elif 'submit_result' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                active_profile = match.player_a if match.player_a and match.player_a.user == user else (match.player_b if match.player_b and match.player_b.user == user else active_profile)
                
                # Marcar mensagens relacionadas como lidas
                from core.models import Message
                Message.objects.filter(related_match=match, recipient=user, is_read=False).update(is_read=True)
                
                # Verifica se o usuário é um dos jogadores e se o jogo está pendente
                if active_profile not in [match.player_a, match.player_b] or match.status != 'pending':
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
                match.reported_by = active_profile
                match.save()
                
                # Envia mensagem para o adversário
                opponent = match.player_b if match.player_a == active_profile else match.player_a
                if opponent and opponent.user:
                    from core.models import Message
                    Message.objects.create(
                        sender=user,
                        recipient=opponent.user,
                        subject="Novo Resultado Lançado",
                        body=f"{active_profile.name} propôs o resultado do jogo {match.tournament.name} do {match.tournament.club.name} (Rodada {match.round_number}). Por favor, avalie esta proposta abaixo (Aceitar ou Recusar e Propor Novo).",
                        related_match=match
                    )
                
                messages.success(request, 'Resultado lançado! Aguardando aprovação do adversário.')
            except Exception as e:
                messages.error(request, f'Erro ao lançar resultado: {str(e)}')
            return redirect(reverse('athlete_dashboard') + '?tab=mensagens')
            
        elif 'accept_result' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                active_profile = match.player_a if match.player_a and match.player_a.user == user else (match.player_b if match.player_b and match.player_b.user == user else active_profile)
                # Marcar mensagens relacionadas como lidas
                from core.models import Message
                Message.objects.filter(related_match=match, recipient=user, is_read=False).update(is_read=True)
                
                if active_profile not in [match.player_a, match.player_b] or match.result_status != 'pending_approval' or match.reported_by == active_profile:
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
                        body=f"{active_profile.name} aceitou o resultado do jogo {match.tournament.name} (Rodada {match.round_number}). O jogo foi finalizado e os pontos computados.",
                        related_match=match
                    )
                    
                messages.success(request, 'Resultado aceito e jogo finalizado!')
            except Exception as e:
                messages.error(request, f'Erro ao aceitar resultado: {str(e)}')
            return redirect(reverse('athlete_dashboard') + '?tab=mensagens')
            
        elif 'mark_message_read' in request.POST:
            msg_id = request.POST.get('message_id')
            try:
                from core.models import Message
                msg = Message.objects.get(id=msg_id, recipient=user)
                msg.is_read = True
                msg.save()
            except:
                pass
            return redirect(reverse('athlete_dashboard') + '?tab=mensagens')
            
        elif 'delete_message' in request.POST:
            msg_id = request.POST.get('message_id')
            try:
                from core.models import Message
                msg = Message.objects.get(id=msg_id, recipient=user)
                msg.delete()
                messages.success(request, 'Mensagem apagada com sucesso.')
            except:
                pass
            return redirect(reverse('athlete_dashboard') + '?tab=mensagens')
    


    # Busca requisições pendentes do usuário focando no clube atual, se houver
    if linked_club:
        pending_request = PlayerLinkRequest.objects.filter(user=user, club=linked_club, status='pending').first()
    else:
        pending_request = PlayerLinkRequest.objects.filter(user=user, status='pending').first()
        
    all_link_requests = PlayerLinkRequest.objects.filter(user=user, status__in=['pending', 'rejected']).select_related('club', 'player')

    # Prepara dados para o select encadeado (Clube -> Atleta)
    clubs = Club.objects.filter(is_visible=True).order_by('name')
    players_data = {}
    for c in clubs:
        players_in_club = Player.objects.filter(club=c, user__isnull=True).exclude(name__icontains='Bye').order_by('name')
        players_data[c.id] = [{'id': p.id, 'name': p.name} for p in players_in_club]

    # Prepara os Jogos do Atleta
    my_matches = []
    my_rankings = []
    my_knockouts = []
    my_tournaments = []
    courts = []
    print(f'DEBUG: club_id_str={club_id_str}, club_id={club_id}, active_profile={active_profile}, linked_club={linked_club}')
    
    if club_id_str == 'all' and my_profiles.exists():
        my_matches = Match.objects.filter(Q(player_a__in=my_profiles) | Q(player_b__in=my_profiles)).select_related('tournament', 'player_a', 'player_b', 'court').order_by('-tournament__current_round', 'round_number')
        
        seen_t = set()
        for m in my_matches:
            if m.tournament and m.tournament.id not in seen_t:
                seen_t.add(m.tournament.id)
                my_tournaments.append(m.tournament)
                if m.tournament.tournament_type == 'ranking':
                    my_rankings.append(m.tournament)
                elif m.tournament.tournament_type == 'knockout':
                    my_knockouts.append(m.tournament)
        
        # When in global view, courts can be from all clubs the user is in.
        # This allows the schedule modal to pick any court.
        # However, the api_court_agenda relies on court.club
        clubs_of_user = my_profiles.values_list('club_id', flat=True)
        courts = Court.objects.filter(club__in=clubs_of_user, is_ranking_court=True)
        
    elif active_profile:
        p = active_profile
        my_matches = Match.objects.filter(Q(player_a=p) | Q(player_b=p)).select_related('tournament', 'player_a', 'player_b', 'court').order_by('-tournament__current_round', 'round_number')
        
        seen_t = set()
        for m in my_matches:
            if m.tournament and m.tournament.id not in seen_t:
                seen_t.add(m.tournament.id)
                my_tournaments.append(m.tournament)
                if m.tournament.tournament_type == 'ranking':
                    my_rankings.append(m.tournament)
                elif m.tournament.tournament_type == 'knockout':
                    my_knockouts.append(m.tournament)
                
        courts = Court.objects.filter(club=linked_club, is_ranking_court=True)

    # Busca Mensagens
    from core.models import Message
    from django.core.paginator import Paginator
    
    user_messages = Message.objects.filter(recipient=user).order_by('-created_at')
    
    msg_date = request.GET.get('msg_date')
    if msg_date:
        try:
            filter_date = datetime.strptime(msg_date, '%Y-%m-%d').date()
            user_messages = user_messages.filter(created_at__date=filter_date)
        except ValueError:
            pass
            
    msg_club_id = request.GET.get('msg_club_id')
    if msg_club_id == 'all' or not msg_club_id:
        pass
    elif msg_club_id:
        try:
            # We filter messages either by their related match club, or if they are broadcast messages (no related match) we just include them for now.
            # But since Broadcast messages don't have a related_match, we can use Q objects to include them if they match or if they have no related_match.
            # For simplicity, if a club is selected, we show messages for that club's matches + broadcast messages without related_match.
            user_messages = user_messages.filter(
                Q(related_match__tournament__club_id=msg_club_id) | Q(related_match__isnull=True)
            )
        except ValueError:
            pass
            
    unread_messages_count = Message.objects.filter(recipient=user, is_read=False).count()
    
    paginator = Paginator(user_messages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    import os
    from django.conf import settings
    avatars_path = os.path.join(settings.BASE_DIR, 'static', 'Avatares')
    try:
        available_avatars = [f for f in os.listdir(avatars_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        available_avatars.sort()
    except FileNotFoundError:
        available_avatars = []

    context = {
        'linked_club': linked_club,
        'user_form': user_form,
        'profile_form': profile_form,
        'link_form': link_form,
        'pending_request': pending_request,
        'all_link_requests': all_link_requests,
        'clubs': clubs,
        'players_json': json.dumps(players_data),
        'my_matches': my_matches,
        'my_tournaments': my_tournaments,
        'my_rankings': my_rankings,
        'my_knockouts': my_knockouts,
        'courts': courts,
        'user_messages': page_obj,
        'athlete_messages': page_obj,
        'unread_messages_count': unread_messages_count,
        'my_player_profile': active_profile or default_profile,
        'my_profiles': my_profiles,
        'available_avatars': available_avatars,
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
            
            local_dt = timezone.localtime(m.scheduled_datetime)
            day = local_dt.day
            if day not in days_data:
                days_data[day] = []
                
            p1_name = m.player_a.name if m.player_a else "TBD"
            p2_name = m.player_b.name if m.player_b else "TBD"
                
            days_data[day].append({
                'id': m.id,
                'title': f"{p1_name} vs {p2_name}",
                'time': local_dt.strftime('%H:%M')
            })
            
        return JsonResponse({'days': days_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def club_landing_page(request):
    if request.method == 'POST':
        from .models import ClubLead
        name = request.POST.get('name')
        club_name = request.POST.get('club_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        if name and club_name and phone:
            ClubLead.objects.create(
                name=name,
                club_name=club_name,
                phone=phone,
                email=email
            )
            messages.success(request, 'Solicitação enviada com sucesso! Entraremos em contato em breve.')
            return redirect('club_landing_page')
        else:
            messages.error(request, 'Por favor, preencha os campos obrigatórios.')
            
    return render(request, 'presentation.html')


@login_required
def athlete_calendar(request):
    user = request.user

    my_profiles = user.player_profiles.all()
    active_profile = my_profiles.first()
    linked_club = active_profile.club if active_profile else None

    my_club_ids = list(set(p.club_id for p in my_profiles if p.club_id))
    my_clubs = Club.objects.filter(id__in=my_club_ids)
    courts = Court.objects.filter(club_id__in=my_club_ids, is_ranking_court=True).select_related('club')

    # ──────────────────────────────────────────────────────────
    # POST: handle schedule_match / delete_schedule / edit_schedule
    # ──────────────────────────────────────────────────────────
    if request.method == 'POST':

        if 'schedule_match' in request.POST:
            match_id = request.POST.get('match_id')
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            end_time_str = request.POST.get('end_time')
            court_id = request.POST.get('court')

            try:
                match = Match.objects.get(id=match_id)
                dt_str = f"{date_str} {time_str}"
                scheduled_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                scheduled_dt = timezone.make_aware(scheduled_dt)

                # Validação de Horário no Passado
                if scheduled_dt < timezone.now():
                    messages.error(request, 'Não é possível agendar um jogo em um horário no passado.')
                    return redirect('athlete_calendar')

                # Validação de Horário de Expediente
                if court_id:
                    try:
                        court_obj = Court.objects.select_related('club').get(id=court_id)
                        club = court_obj.club
                        d = scheduled_dt.weekday()  # 0=Mon, 6=Sun
                        if d == 6:
                            open_t = club.sunday_open
                            close_t = club.sunday_close
                        elif d == 5:
                            open_t = club.saturday_open
                            close_t = club.saturday_close
                        else:
                            open_t = club.weekday_open
                            close_t = club.weekday_close

                        if open_t and close_t:
                            sched_time = scheduled_dt.time()
                            if sched_time < open_t or sched_time > close_t:
                                messages.error(request, f'Horário fora do expediente do clube ({open_t.strftime("%H:%M")} – {close_t.strftime("%H:%M")}).')
                                return redirect('athlete_calendar')
                    except Court.DoesNotExist:
                        pass

                end_dt = None
                if end_time_str:
                    end_dt_str = f"{date_str} {end_time_str}"
                    try:
                        end_dt = timezone.make_aware(datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M"))
                    except ValueError:
                        pass
                
                # Calcular end_dt se não existir (para checagem de conflitos)
                check_end_dt = end_dt
                if not check_end_dt:
                    duration = match.tournament.match_duration if match.tournament and match.tournament.match_duration else 90
                    check_end_dt = scheduled_dt + timedelta(minutes=duration)

                # Checagem de conflitos
                if court_id:
                    conflicts = Match.objects.filter(
                        Q(court_id=court_id) | Q(proposed_court_id=court_id)
                    ).exclude(id=match.id).exclude(schedule_status='pendente')
                    
                    has_conflict = False
                    for c in conflicts:
                        c_start = c.scheduled_datetime or c.proposed_datetime
                        if not c_start: continue
                        c_duration = c.tournament.match_duration if c.tournament and c.tournament.match_duration else 90
                        c_end = c_start + timedelta(minutes=c_duration)
                        if max(scheduled_dt, c_start) < min(check_end_dt, c_end):
                            has_conflict = True
                            break
                            
                    if has_conflict:
                        messages.error(request, 'A quadra selecionada já possui um agendamento ou proposta neste horário.')
                        return redirect('athlete_calendar')

                is_reschedule = match.schedule_status in ['agendado', 'aguardando_adversario']

                # Delete old pending schedule/reschedule messages
                from core.models import Message
                Message.objects.filter(
                    related_match=match,
                    subject__in=["Proposta de Agendamento", "Reagendamento Proposto"]
                ).delete()

                # Clear old scheduled data
                match.scheduled_datetime = None
                match.court = None

                # Save new proposal
                match.proposed_datetime = scheduled_dt
                if court_id:
                    match.proposed_court_id = court_id
                match.proposed_by = active_profile
                match.schedule_status = 'aguardando_adversario'
                match.save()

                # Notify opponent
                opponent = match.player_b if match.player_a == active_profile else match.player_a
                if opponent and opponent.user:
                    court_obj_name = ''
                    if court_id:
                        try:
                            court_obj_name = Court.objects.get(id=court_id).name
                        except Court.DoesNotExist:
                            pass
                    tourn = match.tournament
                    if is_reschedule:
                        subject = "Reagendamento Proposto"
                        body = (
                            f"{active_profile.name} está propondo um REAGENDAMENTO do jogo "
                            f"{tourn.name if tourn else 'Amistoso'} "
                            f"(Rodada {match.round_number}). "
                            f"Nova proposta: {scheduled_dt.strftime('%d/%m/%Y às %H:%M')}"
                            f"{' na ' + court_obj_name if court_obj_name else ''}. "
                            f"O agendamento anterior foi cancelado. "
                            f"Vá para o novo agendamento clicando no botão abaixo."
                        )
                    else:
                        subject = "Proposta de Agendamento"
                        body = (
                            f"{active_profile.name} propôs agendar o jogo "
                            f"{tourn.name if tourn else 'Amistoso'} "
                            f"(Rodada {match.round_number}) "
                            f"para o dia {scheduled_dt.strftime('%d/%m/%Y às %H:%M')}"
                            f"{' na ' + court_obj_name if court_obj_name else ''}. "
                            f"Vá para o novo agendamento clicando no botão abaixo."
                        )
                    Message.objects.create(
                        sender=user,
                        recipient=opponent.user,
                        subject=subject,
                        body=body,
                        related_match=match
                    )

                if is_reschedule:
                    messages.success(request, 'Reagendamento proposto! O adversário foi notificado para confirmar.')
                else:
                    messages.success(request, 'Proposta de agendamento enviada com sucesso ao seu adversário!')

            except Match.DoesNotExist:
                messages.error(request, 'Jogo não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro: {str(e)}')

            return redirect('athlete_calendar')

        elif 'accept_schedule' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                active_profile = match.player_a if match.player_a and match.player_a.user == user else (match.player_b if match.player_b and match.player_b.user == user else active_profile)

                # Marcar mensagens relacionadas como lidas
                from core.models import Message
                Message.objects.filter(related_match=match, recipient=user, is_read=False).update(is_read=True)

                # Verifica se a pessoa logada é realmente do jogo
                if active_profile not in [match.player_a, match.player_b]:
                    messages.error(request, 'Permissão negada.')
                    return redirect('athlete_calendar')

                if match.schedule_status != 'aguardando_adversario':
                    messages.error(request, 'Não há proposta pendente para este jogo.')
                    return redirect('athlete_calendar')

                # Checa conflitos de forma precisa
                check_start = match.proposed_datetime
                duration = match.tournament.match_duration if match.tournament and match.tournament.match_duration else 90
                check_end = check_start + timedelta(minutes=duration)

                conflicts = Match.objects.filter(
                    Q(court=match.proposed_court) | Q(proposed_court=match.proposed_court)
                ).exclude(id=match.id).exclude(schedule_status='pendente')

                has_conflict = False
                for c in conflicts:
                    c_start = c.scheduled_datetime or c.proposed_datetime
                    if not c_start: continue
                    c_duration = c.tournament.match_duration if c.tournament and c.tournament.match_duration else 90
                    c_end = c_start + timedelta(minutes=c_duration)
                    if max(check_start, c_start) < min(check_end, c_end):
                        has_conflict = True
                        break

                if has_conflict:
                    messages.error(request, 'A quadra não está mais disponível neste horário. Por favor, recuse e proponha um novo horário.')
                else:
                    match.scheduled_datetime = match.proposed_datetime
                    match.court = match.proposed_court
                    match.schedule_status = 'agendado'
                    match.save()

                    if match.proposed_by and match.proposed_by.user:
                        local_dt = timezone.localtime(match.scheduled_datetime)
                        Message.objects.create(
                            sender=user,
                            recipient=match.proposed_by.user,
                            subject="Agendamento Aceito!",
                            body=f"{active_profile.name} aceitou sua proposta! O jogo {match.tournament.name} do {match.tournament.club.name} foi marcado para {local_dt.strftime('%d/%m/%Y às %H:%M')} na {match.court.name}.",
                            related_match=match
                        )
                    messages.success(request, 'Agendamento confirmado com sucesso!')
            except Match.DoesNotExist:
                messages.error(request, 'Jogo não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro: {str(e)}')

            return redirect('athlete_calendar')


        elif 'delete_schedule' in request.POST:
            match_id = request.POST.get('match_id')
            try:
                match = Match.objects.get(id=match_id)
                match.scheduled_datetime = None
                match.proposed_datetime = None
                match.proposed_court = None
                match.schedule_status = 'unagendado'
                match.save()
                messages.success(request, 'Agendamento excluído com sucesso.')
            except Match.DoesNotExist:
                messages.error(request, 'Jogo não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro: {str(e)}')
            return redirect('athlete_calendar')

    # ──────────────────────────────────────────────────────────
    # GET: build context
    # ──────────────────────────────────────────────────────────
    my_profile_ids = set(p.id for p in my_profiles)

    # User's own matches
    my_matches = Match.objects.filter(
        Q(player_a=active_profile) | Q(player_b=active_profile)
    ).select_related('tournament', 'player_a', 'player_b', 'court', 'proposed_court', 'winner').order_by('-tournament__current_round', 'round_number') if active_profile else Match.objects.none()

    # All scheduled matches at user's clubs (for occupation view)
    all_club_matches = Match.objects.filter(
        Q(tournament__club_id__in=my_club_ids) &
        (Q(scheduled_datetime__isnull=False) | Q(proposed_datetime__isnull=False))
    ).select_related('tournament', 'tournament__club', 'player_a', 'player_b', 'court', 'proposed_court', 'winner')

    # Standby matches: current round, not scheduled, not Bye
    standby_matches = []
    future_matches = []
    if active_profile:
        for m in my_matches:
            if m.schedule_status not in ['pendente', 'unagendado']:
                continue
            if m.status == 'completed' or (m.tournament and m.tournament.is_finished):
                continue
            p1_name = m.player_a.name if m.player_a else 'A definir'
            p2_name = m.player_b.name if m.player_b else 'A definir'
            
            if 'bye' in p1_name.lower() or 'bye' in p2_name.lower():
                continue
            adversary = p2_name if m.player_a_id in my_profile_ids else p1_name
            
            match_data = {
                'id': m.id,
                'title': f"{p1_name} vs {p2_name}",
                'adversary': adversary,
                'tournament': m.tournament.name if m.tournament else '',
                'round': m.round_number if hasattr(m, 'round_number') else '',
                'club_name': m.tournament.club.name if m.tournament and m.tournament.club else '',
                'duration': m.tournament.match_duration if m.tournament and m.tournament.match_duration else 90,
                'club_id': m.tournament.club_id if m.tournament else None,
                'allow_player_scheduling': m.tournament.allow_player_scheduling if m.tournament else True,
            }
            
            if m.tournament and m.round_number != m.tournament.current_round:
                future_matches.append(match_data)
            else:
                standby_matches.append(match_data)

    # Build matches_json (user's own matches for calendar display)
    matches_json = []
    for m in my_matches:
        dt = m.scheduled_datetime if m.scheduled_datetime else m.proposed_datetime
        if not dt:
            continue
        court = m.court if m.court else m.proposed_court
        court_name_str = f' na {court.name}' if court else ''
        tourn_name = m.tournament.name if m.tournament else 'Amistoso'
        club_name = m.tournament.club.name if m.tournament and m.tournament.club else (linked_club.name if linked_club else '')
        if m.schedule_status in ['agendado', 'aguardando_adversario']:
            status_display = m.schedule_status.upper().replace('_', ' ')
        else:
            status_display = 'AGENDADO PELO ADM'

        round_info = ""
        if m.tournament:
            if getattr(m, 'phase', None):
                round_info = f" // {m.phase}"
            elif getattr(m, 'round_number', None):
                round_info = f" // Rodada {m.round_number}"

        p1_name = m.player_a.name if m.player_a else 'A definir'
        p2_name = m.player_b.name if m.player_b else 'A definir'
        title = f"{p1_name} vs {p2_name} // {tourn_name}{round_info} // {club_name}"
        duration = m.tournament.match_duration if m.tournament and m.tournament.match_duration else 90
        local_dt = timezone.localtime(dt)
        
        is_completed = m.status == 'completed'
        score_str = ""
        date_str_br = local_dt.strftime('%d/%m/%Y')
        if is_completed:
            winner_name = m.winner.name if m.winner else "Desconhecido"
            sets_scores = []
            for a, b in [(m.set1_a, m.set1_b), (m.set2_a, m.set2_b), (m.set3_a, m.set3_b), (m.set4_a, m.set4_b), (m.set5_a, m.set5_b)]:
                if a is not None and b is not None:
                    sets_scores.append(f"{a}-{b}")
            score_text = ", ".join(sets_scores)
            
            if score_text and m.sets_a is not None and m.sets_b is not None:
                score_str = f"VITÓRIA de {winner_name} por {m.sets_a}x{m.sets_b} | {score_text}"
            elif m.sets_a is not None and m.sets_b is not None:
                score_str = f"VITÓRIA de {winner_name} por {m.sets_a}x{m.sets_b}"
            else:
                score_str = f"VITÓRIA de {winner_name} por W.O."
            
        matches_json.append({
            'id': m.id,
            'title': title,
            'status_display': status_display,
            'start': local_dt.isoformat(),
            'end': (local_dt + timedelta(minutes=duration)).isoformat(),
            'status': m.schedule_status,
            'match_status': m.status,
            'is_mine': True,
            'is_completed': is_completed,
            'score_str': score_str,
            'date_str_br': date_str_br,
            'court_id': court.id if court else None,
            'court_name': court.name if court else '',
            'tournament': tourn_name,
            'club_id': m.tournament.club_id if m.tournament else None,
            'duration': duration,
            'adversary': m.player_b.name if m.player_a_id in my_profile_ids else m.player_a.name,
            'can_accept': m.schedule_status == 'aguardando_adversario' and m.proposed_by_id and m.proposed_by_id not in my_profile_ids,
            'allow_player_scheduling': m.tournament.allow_player_scheduling if m.tournament else True,
            'is_tournament_finished': m.tournament.is_finished if m.tournament else False,
        })

    # Build all_matches_json (all club matches for occupation display)
    all_matches_json = []
    for m in all_club_matches:
        is_mine = m.player_a_id in my_profile_ids or m.player_b_id in my_profile_ids
        dt = m.scheduled_datetime if m.scheduled_datetime else m.proposed_datetime
        if not dt:
            continue
        court = m.court if m.court else m.proposed_court
        tourn_name = m.tournament.name if m.tournament else 'Amistoso'
        club_name = m.tournament.club.name if m.tournament and m.tournament.club else ''
        if m.schedule_status in ['agendado', 'aguardando_adversario']:
            status_display = m.schedule_status.upper().replace('_', ' ')
        else:
            status_display = 'AGENDADO PELO ADM'

        round_info = ""
        if m.tournament:
            if getattr(m, 'phase', None):
                round_info = f" // {m.phase}"
            elif getattr(m, 'round_number', None):
                round_info = f" // Rodada {m.round_number}"
        pa_name = m.player_a.name if m.player_a else "A definir"
        pb_name = m.player_b.name if m.player_b else "A definir"
        title = f"{pa_name} vs {pb_name} // {tourn_name}{round_info} // {club_name}"
        duration = m.tournament.match_duration if m.tournament and m.tournament.match_duration else 90
        local_dt = timezone.localtime(dt)
        
        is_completed = m.status == 'completed'
        score_str = ""
        date_str_br = local_dt.strftime('%d/%m/%Y')
        if is_completed:
            winner_name = m.winner.name if m.winner else "Desconhecido"
            sets_scores = []
            for a, b in [(m.set1_a, m.set1_b), (m.set2_a, m.set2_b), (m.set3_a, m.set3_b), (m.set4_a, m.set4_b), (m.set5_a, m.set5_b)]:
                if a is not None and b is not None:
                    sets_scores.append(f"{a}-{b}")
            score_text = ", ".join(sets_scores)
            
            if score_text and m.sets_a is not None and m.sets_b is not None:
                score_str = f"VITÓRIA de {winner_name} por {m.sets_a}x{m.sets_b} | {score_text}"
            elif m.sets_a is not None and m.sets_b is not None:
                score_str = f"VITÓRIA de {winner_name} por {m.sets_a}x{m.sets_b}"
            else:
                score_str = f"VITÓRIA de {winner_name} por W.O."
            
        all_matches_json.append({
            'id': m.id,
            'title': title,
            'status_display': status_display,
            'start': local_dt.isoformat(),
            'end': (local_dt + timedelta(minutes=duration)).isoformat(),
            'status': m.schedule_status,
            'match_status': m.status,
            'is_mine': is_mine,
            'is_completed': is_completed,
            'score_str': score_str,
            'date_str_br': date_str_br,
            'court_id': court.id if court else None,
            'court_name': court.name if court else '',
            'club_id': m.tournament.club_id if m.tournament else None,
            'club_name': club_name,
            'duration': duration,
            'can_accept': m.schedule_status == 'aguardando_adversario' and m.proposed_by_id and m.proposed_by_id not in my_profile_ids,
            'allow_player_scheduling': m.tournament.allow_player_scheduling if m.tournament else True,
        })

    # Club opening hours for frontend validation
    clubs_hours_json = {}
    for c in Club.objects.filter(id__in=my_club_ids):
        clubs_hours_json[c.id] = {
            'weekday_open': c.weekday_open.strftime('%H:%M') if c.weekday_open else None,
            'weekday_close': c.weekday_close.strftime('%H:%M') if c.weekday_close else None,
            'saturday_open': c.saturday_open.strftime('%H:%M') if hasattr(c, 'saturday_open') and c.saturday_open else None,
            'saturday_close': c.saturday_close.strftime('%H:%M') if hasattr(c, 'saturday_close') and c.saturday_close else None,
            'sunday_open': c.sunday_open.strftime('%H:%M') if hasattr(c, 'sunday_open') and c.sunday_open else None,
            'sunday_close': c.sunday_close.strftime('%H:%M') if hasattr(c, 'sunday_close') and c.sunday_close else None,
        }

    context = {
        'my_profiles': my_profiles,
        'active_profile': active_profile,
        'linked_club': linked_club,
        'my_clubs': my_clubs,
        'courts': courts,
        'matches_json': json.dumps(matches_json),
        'all_matches_json': json.dumps(all_matches_json),
        'standby_matches': standby_matches,
        'standby_matches_json': json.dumps(standby_matches),
        'future_matches_json': json.dumps(future_matches),
        'clubs_hours_json': json.dumps(clubs_hours_json),
    }
    return render(request, 'athlete_calendar.html', context)

@login_required
def athlete_stats(request):
    if hasattr(request.user, 'role') and request.user.role == 'club_admin':
        return redirect('club_dashboard')

    my_profiles = getattr(request.user, 'player_profiles', None)
    if not my_profiles or not my_profiles.exists():
        from django.contrib import messages
        messages.info(request, "Você ainda não possui um perfil de atleta vinculado.")
        return redirect('home')

    profile_id = request.GET.get('profile_id')
    if profile_id:
        active_profiles = [get_object_or_404(Player, id=profile_id, user=request.user)]
        active_profile = active_profiles[0] # keep for compatibility with template if needed
    else:
        active_profiles = list(my_profiles.all())
        active_profile = active_profiles[0] if active_profiles else None

    from django.db.models import Q
    from clubs.models import Match, CategoryPlayer, Tournament
    import json
    import re
    
    matches = Match.objects.filter(Q(player_a__in=active_profiles) | Q(player_b__in=active_profiles)).order_by('-id')
    
    total_matches = matches.filter(status='completed').count()
    wins = matches.filter(status='completed', winner__in=active_profiles).count()
    losses = total_matches - wins
    win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

    completed_matches = list(matches.filter(status='completed'))
    
    def get_chrono_key(m):
        m_ord = 0
        if getattr(m, 'scheduled_datetime', None):
            m_ord = m.scheduled_datetime.toordinal()
            
        t_ord = 0
        if m.tournament and getattr(m.tournament, 'start_date', None):
            t_ord = m.tournament.start_date.toordinal()
            
        if not t_ord:
            t_ord = m_ord
            
        if not t_ord:
            # Fallback para torneios sem data: o usuário relatou que IDs maiores são mais antigos
            t_ord = -(m.tournament_id or 0)
            
        r_num = getattr(m, 'round_number', 0) or 0
        return (t_ord, m_ord, r_num, m.id)

    # Ordena de forma crescente (Mais Antigo -> Mais Novo)
    completed_matches.sort(key=get_chrono_key)
    # Pega apenas os últimos 15 (que são os 15 mais novos) mantendo a ordem crescente
    last_15 = completed_matches[-15:]
    
    # Preenche com None no FINAL da lista até ter 15 jogos
    while len(last_15) < 15:
        last_15.append(None)

    chart_labels = []
    chart_data = []
    chart_details = []
    for idx, m in enumerate(last_15):
        chart_labels.append(f"J{idx+1}")
        
        if m is None:
            chart_data.append(None)
            chart_details.append({
                'opponent': '-',
                'tournament': '-',
                'result': 'Sem dados'
            })
            continue

        if m.winner in active_profiles:
            chart_data.append(1)
            result_text = "Vitória"
        else:
            chart_data.append(-1)
            result_text = "Derrota"
            
        opponent = m.player_b if m.player_a in active_profiles else m.player_a
        opponent_name = opponent.name if opponent else "Desconhecido"
        tournament_name = m.tournament.name if m.tournament else "Amistoso"
        club_name = m.tournament.club.name if m.tournament and m.tournament.club else "-"
        
        chart_details.append({
            'opponent': opponent_name,
            'tournament': tournament_name,
            'result': result_text,
            'club': club_name
        })
            
    cat_players = CategoryPlayer.objects.filter(player__in=active_profiles).select_related('category', 'category__tournament')
    active_tournaments = list(cat_players.filter(category__tournament__is_finished=False).order_by('-id'))
    
    for cp in active_tournaments:
        if cp.category.tournament.tournament_type == 'ranking':
            cp.current_rank = CategoryPlayer.objects.filter(category=cp.category).filter(
                Q(points__gt=cp.points) | 
                (Q(points=cp.points) & Q(wins__gt=cp.wins))
            ).count() + 1
        else:
            cp.current_rank = None

    finished_tournaments = cat_players.filter(category__tournament__is_finished=True).order_by('-category__tournament__id')
    
    finished_data = []
    titles = 0
    for cp in finished_tournaments:
        t = cp.category.tournament
        phase = ""
        is_champion = False
        
        if t.tournament_type == 'ranking':
            rank = CategoryPlayer.objects.filter(category=cp.category).filter(
                Q(points__gt=cp.points) | 
                (Q(points=cp.points) & Q(wins__gt=cp.wins))
            ).count() + 1
            phase = f"{rank}º Lugar"
            if rank == 1:
                is_champion = True
                titles += 1
        else:
            last_match = Match.objects.filter(
                tournament=t, category=cp.category, status='completed'
            ).filter(Q(player_a__in=active_profiles) | Q(player_b__in=active_profiles)).order_by('round_number').first()
            
            if last_match:
                r = last_match.round_number
                if r == 1:
                    phase = "Campeão" if last_match.winner in active_profiles else "Vice-Campeão"
                    if last_match.winner in active_profiles:
                        is_champion = True
                        titles += 1
                elif r == 2: phase = "Semifinal"
                elif r == 3: phase = "Quartas de Final"
                elif r == 4: phase = "Oitavas de Final"
                else: phase = f"Fase de 1/{2**(r-1)}"
            else:
                phase = "Não jogou"

        finished_data.append({
            'tournament': t,
            'category': cp.category,
            'phase': phase,
            'is_champion': is_champion
        })

    recurring_dict = {}
    for cp in finished_tournaments:
        t = cp.category.tournament
        base_name = re.sub(r'\s*\d{4}\s*', '', t.name).strip()
        year_match = re.search(r'\d{4}', t.name)
        year = year_match.group(0) if year_match else "Geral"
        
        phase = next((d['phase'] for d in finished_data if d['tournament'] == t), "")
        
        if base_name not in recurring_dict:
            recurring_dict[base_name] = []
        recurring_dict[base_name].append({'year': year, 'phase': phase, 't_name': t.name})
        
    recurring_comparison = {k: v for k, v in recurring_dict.items() if len(v) > 1}

    context = {
        'my_profiles': my_profiles.all(),
        'active_profile': active_profile,
        'total_matches': total_matches,
        'wins': wins,
        'losses': losses,
        'win_rate': round(win_rate, 1),
        'titles': titles,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'chart_details': json.dumps(chart_details),
        'active_tournaments': active_tournaments,
        'finished_data': finished_data,
        'recurring_comparison': recurring_comparison,
    }
    return render(request, 'athlete_stats.html', context)
