from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import News
from clubs.models import Club

@require_POST
def like_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    
    if request.user.is_authenticated:
        if request.user in news.likes.all():
            news.likes.remove(request.user)
            liked = False
        else:
            news.likes.add(request.user)
            liked = True
    else:
        # Visitante anônimo usando session
        liked_news = request.session.get('liked_news', [])
        if news.id in liked_news:
            liked_news.remove(news.id)
            news.anonymous_likes = max(0, news.anonymous_likes - 1)
            liked = False
        else:
            liked_news.append(news.id)
            news.anonymous_likes += 1
            liked = True
        
        request.session['liked_news'] = liked_news
        news.save(update_fields=['anonymous_likes'])

    return JsonResponse({'liked': liked, 'total_likes': news.get_total_likes})

from django.db.models import Q

def _get_liked_news_ids(request):
    if request.user.is_authenticated:
        return list(request.user.news_likes.values_list('id', flat=True))
    return request.session.get('liked_news', [])

def news_global_list(request):
    """Lista as noticias globais do AllCourts365 (sem clube ou flag is_global=True, e publicadas)."""
    news_qs = News.objects.filter(Q(club__isnull=True) | Q(is_global=True), is_published=True).order_by("-published_at")
    paginator = Paginator(news_qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "news_list.html", {
        "page_obj": page_obj,
        "page_title": "Noticias AllCourts365",
        "club": None,
        "liked_news_ids": _get_liked_news_ids(request),
    })

def news_club_list(request, club_id):
    """Lista as noticias de um clube especifico."""
    club = get_object_or_404(Club, id=club_id)
    news_qs = News.objects.filter(is_published=True, club=club).order_by("-published_at")
    paginator = Paginator(news_qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "news_list.html", {
        "page_obj": page_obj,
        "page_title": f"Noticias {club.name}",
        "club": club,
        "liked_news_ids": _get_liked_news_ids(request),
    })

def news_detail(request, slug, club_id=None):
    """Detalhe de uma noticia."""
    news = get_object_or_404(News, slug=slug, is_published=True)
    club = news.club
    return render(request, "news_detail.html", {
        "news": news,
        "club": club,
        "liked_news_ids": _get_liked_news_ids(request),
    })
