from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import Q
from .models import Club, Match
import os

def club_list(request):
    clubs = Club.objects.all().order_by('name')
    return render(request, 'club_list.html', {'clubs': clubs})

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
    club       = get_object_or_404(Club, id=club_id)
    tournament = get_object_or_404(club.tournaments, id=tournament_id, tournament_type='knockout', is_active=True)
    categories = tournament.categories.all()
    return render(request, 'knockout_detail.html', {
        'club':       club,
        'tournament': tournament,
        'categories': categories,
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

    return render(request, 'knockout_bracket.html', {
        'club':       club,
        'tournament': tournament,
        'category':   category,
        'brackets':   brackets_list,
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
