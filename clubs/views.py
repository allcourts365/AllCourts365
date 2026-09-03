from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Club

def club_list(request):
    clubs = Club.objects.all().order_by('name')
    return render(request, 'club_list.html', {'clubs': clubs})

def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    rankings = club.tournaments.filter(is_active=True, tournament_type='ranking')
    knockouts = club.tournaments.filter(is_active=True, tournament_type='knockout')
    return render(request, 'club_detail.html', {'club': club, 'rankings': rankings, 'knockouts': knockouts})

def ranking_detail(request, club_id, ranking_id):
    club = get_object_or_404(Club, id=club_id)
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
