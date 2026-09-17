from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.db.models import Q
from .models import Club, Match
import os

def club_list(request):
    clubs = Club.objects.filter(is_visible=True).order_by('name')
    return render(request, 'club_list.html', {'clubs': clubs})

@xframe_options_sameorigin
def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    rankings  = club.tournaments.filter(is_active=True, tournament_type='ranking')
    knockouts = club.tournaments.filter(is_active=True, tournament_type='knockout')
    return render(request, 'club_detail.html', {
        'club': club,
        'rankings': rankings,
        'knockouts': knockouts,
    })

def ranking_detail(request, club_id, ranking_id):
    club    = get_object_or_404(Club, id=club_id)
    ranking = get_object_or_404(club.tournaments, id=ranking_id, tournament_type='ranking', is_active=True)

    categories = ranking.categories.all()

    data = {}
    for cat in categories:
        players = cat.players.exclude(Q(player__name__icontains='bye') | Q(player__name__icontains='folga'))
        matches = cat.matches.all().order_by('round_number')

        rounds_dict = {}
        for m in matches:
            if m.round_number not in rounds_dict:
                rounds_dict[m.round_number] = []
            rounds_dict[m.round_number].append(m)

        data[cat] = {
            'players': players,
            'rounds': rounds_dict
        }

    return render(request, 'ranking_detail.html', {'club': club, 'ranking': ranking, 'data': data})


# ── Torneios Eliminatórios ─────────────────────────────────────────────────────

def knockout_detail(request, club_id, tournament_id):
    """Página principal do torneio eliminatório — exibe os cards de categorias."""
    from .models import Match, CategoryPlayer
    club       = get_object_or_404(Club, id=club_id)
    tournament = get_object_or_404(club.tournaments, id=tournament_id, tournament_type='knockout', is_active=True)
    categories = tournament.categories.all()
    
    # Busca todos os jogos agendados do torneio inteiro
    scheduled_matches = list(Match.objects.filter(tournament=tournament, schedule_status='agendado').order_by('scheduled_datetime', 'court_id'))
    
    # Calcula os match_numbers baseado nas chaves
    all_tourn_matches = list(Match.objects.filter(tournament=tournament).order_by('category_id', 'round_number', 'position_in_bracket'))
    match_counter_by_cat = {}
    match_number_map = {}
    for m in all_tourn_matches:
        if m.category_id not in match_counter_by_cat:
            match_counter_by_cat[m.category_id] = 1
        match_number_map[m.id] = match_counter_by_cat[m.category_id]
        match_counter_by_cat[m.category_id] += 1
        
    for sm in scheduled_matches:
        sm.match_number = match_number_map.get(sm.id, sm.id)
    
    # Busca todos os atletas inscritos no torneio
    all_participants = CategoryPlayer.objects.filter(category__tournament=tournament).select_related('player', 'category').order_by('player__name')
    
    return render(request, 'knockout_detail.html', {
        'club':       club,
        'tournament': tournament,
        'categories': categories,
        'scheduled_matches': scheduled_matches,
        'all_participants': all_participants,
    })


def knockout_bracket(request, club_id, tournament_id, category_id):
    """Página de visualização do chaveamento de uma categoria no formato TC22A."""
    club       = get_object_or_404(Club, id=club_id)
    tournament = get_object_or_404(club.tournaments, id=tournament_id, tournament_type='knockout', is_active=True)
    category   = get_object_or_404(tournament.categories, id=category_id)

    all_matches = list(Match.objects.filter(category=category, tournament=tournament)
                       .select_related('player_a', 'player_b', 'winner')
                       .order_by('round_number', 'position_in_bracket'))

    match_by_id = {}
    children_by_next_match = {}
    rounds_dict = {}

    # Label (Chaves) - Opcional, caso number_of_brackets seja adicionado no futuro
    num_brackets = getattr(tournament, 'number_of_brackets', 1)
    if num_brackets > 1:
        r1_matches = [m for m in all_matches if m.round_number == 1]
        total_r1 = len(r1_matches)
        if total_r1 > 0:
            matches_per_bracket = total_r1 // num_brackets
            if matches_per_bracket > 0:
                for m in r1_matches:
                    idx = m.position_in_bracket - 1
                    if idx % matches_per_bracket == 0:
                        m.bracket_label = f"Chave { (idx // matches_per_bracket) + 1 }"

    match_counter = 1
    for m in all_matches:
        m.match_number = match_counter
        match_by_id[m.id] = m
        match_counter += 1
        
        if m.next_match_id:
            if m.next_match_id not in children_by_next_match:
                children_by_next_match[m.next_match_id] = []
            children_by_next_match[m.next_match_id].append(m)
            
        if m.round_number not in rounds_dict:
            rounds_dict[m.round_number] = []
        rounds_dict[m.round_number].append(m)

    for m in all_matches:
        m.prev_match_a = None
        m.prev_match_b = None
        if m.id in children_by_next_match:
            for prev in children_by_next_match[m.id]:
                if prev.position_in_bracket % 2 != 0:
                    m.prev_match_a = prev
                else:
                    m.prev_match_b = prev

    brackets_list = []
    if all_matches:
        brackets_list.append({
            'name': category.name,
            'rounds': rounds_dict
        })

    scheduled_matches = list(Match.objects.filter(category=category, schedule_status='agendado').order_by('scheduled_datetime'))

    return render(request, 'knockout_bracket.html', {
        'club':       club,
        'tournament': tournament,
        'category':   category,
        'brackets':   brackets_list,
        'scheduled_matches': scheduled_matches,
    })

def knockout_general_ranking(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    from .models import Category, CategoryPlayer
    from django.db.models import Count, Sum
    
    categories_names = list(Category.objects.filter(
        tournament__club=club, 
        tournament__tournament_type='knockout', 
        tournament__is_active=True
    ).values_list('name', flat=True).distinct().order_by('name'))
    
    selected_category = request.GET.get('categoria')
    if not selected_category and categories_names:
        selected_category = categories_names[0]
        
    category_counts = CategoryPlayer.objects.filter(
        category__tournament__club=club,
        category__tournament__tournament_type='knockout',
        category__tournament__is_active=True,
        category__tournament__is_finished=True
    ).values('category__name').annotate(player_count=Count('player', distinct=True))
    cat_counts_dict = {item['category__name']: item['player_count'] for item in category_counts}
    
    categories_with_counts = []
    for name in categories_names:
        categories_with_counts.append({
            'name': name,
            'count': cat_counts_dict.get(name, 0)
        })
        
    ranking_data = []
    if selected_category:
        ranking_data = CategoryPlayer.objects.filter(
            category__tournament__club=club,
            category__tournament__tournament_type='knockout',
            category__name=selected_category,
            category__tournament__is_active=True,
            category__tournament__is_finished=True
        ).values(
            'player__name', 'player__id'
        ).annotate(
            total_points=Sum('points'),
            total_matches=Sum('matches_played'),
            total_wins=Sum('wins'),
            total_losses=Sum('losses')
        ).order_by('-total_points', '-total_wins', 'total_matches')
        
    return render(request, 'knockout_general_ranking.html', {
        'club': club,
        'categories': categories_with_counts,
        'selected_category': selected_category,
        'ranking_data': ranking_data,
    })


def download_knockout_template(request):
    """Serve a planilha modelo para download."""
    from django.conf import settings
    filepath = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'planilha_torneio.xlsx')
    # Fallback: busca relativo à raiz do projeto
    if not os.path.exists(filepath):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base, 'static', 'planilha_torneio.xlsx')
    if not os.path.exists(filepath):
        raise Http404("Planilha modelo não encontrada.")
    return FileResponse(open(filepath, 'rb'), as_attachment=True, filename='planilha_torneio.xlsx')

from django.contrib import messages
from django.shortcuts import redirect
from .scheduling import generate_knockout_schedule
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def generate_schedule_view(request, club_id, tournament_id):
    if request.method == 'POST':
        success, msg = generate_knockout_schedule(tournament_id)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
    return redirect('clubs:knockout_detail', club_id=club_id, tournament_id=tournament_id)

def knockout_schedule_print(request, club_id, tournament_id):
    """View read-only para impressão da programação do torneio."""
    from .models import Match, CategoryPlayer, Club
    club       = get_object_or_404(Club, id=club_id)
    tournament = get_object_or_404(club.tournaments, id=tournament_id, tournament_type='knockout', is_active=True)
    
    # Busca todos os jogos agendados
    scheduled_matches = list(Match.objects.filter(tournament=tournament, schedule_status='agendado').order_by('scheduled_datetime', 'court_id'))
    
    # Calcula os match_numbers
    all_tourn_matches = list(Match.objects.filter(tournament=tournament).order_by('category_id', 'round_number', 'position_in_bracket'))
    match_counter_by_cat = {}
    match_number_map = {}
    for m in all_tourn_matches:
        if m.category_id not in match_counter_by_cat:
            match_counter_by_cat[m.category_id] = 1
        match_number_map[m.id] = match_counter_by_cat[m.category_id]
        match_counter_by_cat[m.category_id] += 1
        
    for sm in scheduled_matches:
        sm.match_number = match_number_map.get(sm.id, sm.id)
        
    return render(request, 'knockout_schedule_print.html', {
        'club': club,
        'tournament': tournament,
        'scheduled_matches': scheduled_matches,
        'total_matches': len(scheduled_matches),
    })

def knockout_bracket_print(request, club_id, tournament_id, category_id):
    """View read-only para impressão do chaveamento de uma categoria."""
    from .models import Club, Match
    club       = get_object_or_404(Club, id=club_id)
    tournament = get_object_or_404(club.tournaments, id=tournament_id, tournament_type='knockout', is_active=True)
    category   = get_object_or_404(tournament.categories, id=category_id)

    all_matches = list(Match.objects.filter(category=category, tournament=tournament)
                       .select_related('player_a', 'player_b', 'winner')
                       .order_by('round_number', 'position_in_bracket'))

    match_by_id = {}
    children_by_next_match = {}
    rounds_dict = {}

    num_brackets = getattr(tournament, 'number_of_brackets', 1)
    if num_brackets > 1:
        r1_matches = [m for m in all_matches if m.round_number == 1]
        total_r1 = len(r1_matches)
        if total_r1 > 0:
            matches_per_bracket = total_r1 // num_brackets
            if matches_per_bracket > 0:
                for m in r1_matches:
                    idx = m.position_in_bracket - 1
                    if idx % matches_per_bracket == 0:
                        m.bracket_label = f"Chave { (idx // matches_per_bracket) + 1 }"

    match_counter = 1
    for m in all_matches:
        m.match_number = match_counter
        match_by_id[m.id] = m
        match_counter += 1
        
        if m.next_match_id:
            if m.next_match_id not in children_by_next_match:
                children_by_next_match[m.next_match_id] = []
            children_by_next_match[m.next_match_id].append(m)
            
        if m.round_number not in rounds_dict:
            rounds_dict[m.round_number] = []
        rounds_dict[m.round_number].append(m)

    for m in all_matches:
        m.prev_match_a = None
        m.prev_match_b = None
        if m.id in children_by_next_match:
            for prev in children_by_next_match[m.id]:
                if prev.position_in_bracket % 2 != 0:
                    m.prev_match_a = prev
                else:
                    m.prev_match_b = prev

    brackets_list = []
    if all_matches:
        all_round_numbers = sorted(rounds_dict.keys())
        max_rounds = 4
        max_initial_matches = 8
        page_index = 1
        
        for round_start_idx in range(0, len(all_round_numbers), max_rounds):
            chunk_rounds = all_round_numbers[round_start_idx : round_start_idx + max_rounds]
            first_round_in_chunk = chunk_rounds[0]
            first_round_matches = rounds_dict[first_round_in_chunk]
            
            for match_start_idx in range(0, len(first_round_matches), max_initial_matches):
                chunk_matches = first_round_matches[match_start_idx : match_start_idx + max_initial_matches]
                
                page_rounds_dict = {}
                page_rounds_dict[first_round_in_chunk] = chunk_matches
                
                current_layer_matches = chunk_matches
                for r in chunk_rounds[1:]:
                    next_layer_set = {m.next_match_id: True for m in current_layer_matches if m.next_match_id}
                    next_layer_matches = [m for m in rounds_dict.get(r, []) if m.id in next_layer_set]
                    if not next_layer_matches:
                        break
                    page_rounds_dict[r] = next_layer_matches
                    current_layer_matches = next_layer_matches
                    
                brackets_list.append({
                    'name': f"{category.name} - Parte {page_index}",
                    'rounds': page_rounds_dict
                })
                page_index += 1
                
        if len(brackets_list) == 1:
            brackets_list[0]['name'] = category.name

    return render(request, 'knockout_bracket_print.html', {
        'club':       club,
        'tournament': tournament,
        'category':   category,
        'brackets':   brackets_list,
    })
