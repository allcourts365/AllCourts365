from django.shortcuts import render, get_object_or_404
from .models import Club

def club_list(request):
    clubs = Club.objects.all().order_by('name')
    return render(request, 'club_list.html', {'clubs': clubs})

def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    tournaments = club.tournaments.filter(is_active=True)
    return render(request, 'club_detail.html', {'club': club, 'tournaments': tournaments})
