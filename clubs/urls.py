from django.urls import path
from . import views
from news import views as news_views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='list'),
    path('<int:club_id>/', views.club_detail, name='detail'),
    path('<int:club_id>/departamento/<int:department_id>/', views.department_detail, name='department_detail'),
    path('<int:club_id>/season/<int:ranking_id>/', views.ranking_detail, name='ranking_detail'),
    path('<int:club_id>/eliminatory/<int:tournament_id>/', views.knockout_detail, name='knockout_detail'),
    path('<int:club_id>/eliminatory/<int:tournament_id>/categoria/<int:category_id>/', views.knockout_bracket, name='knockout_bracket'),
    path('<int:club_id>/eliminatory/<int:tournament_id>/categoria/<int:category_id>/print-bracket/', views.knockout_bracket_print, name='knockout_bracket_print'),
    path('<int:club_id>/ranking-eliminatorio/', views.knockout_general_ranking, name='knockout_general_ranking'),
    path('<int:club_id>/eliminatory/<int:tournament_id>/gerar-programacao/', views.generate_schedule_view, name='generate_schedule'),
    path('<int:club_id>/eliminatory/<int:tournament_id>/print-schedule/', views.knockout_schedule_print, name='knockout_schedule_print'),
    path('download/modelo-torneio/', views.download_knockout_template, name='download_knockout_template'),
    # Noticias por clube
    path('<int:club_id>/noticias/', news_views.news_club_list, name='news_list'),
    path('<int:club_id>/noticias/<slug:slug>/', news_views.news_detail, name='news_detail'),
    
    # Inscrição em Torneio
    path('<int:club_id>/torneio/<int:tournament_id>/inscricao/passo-1/', views.registration_step1, name='registration_step1'),
    path('<int:club_id>/torneio/<int:tournament_id>/inscricao/passo-2/', views.registration_step2, name='registration_step2'),
    path('<int:club_id>/torneio/<int:tournament_id>/inscricao/passo-3/', views.registration_step3, name='registration_step3'),
    path('<int:club_id>/torneio/<int:tournament_id>/inscricao/sucesso/', views.registration_success, name='registration_success'),
    path('<int:club_id>/torneio/<int:tournament_id>/inscricao/resumo/<int:cp_id>/', views.registration_resume, name='registration_resume'),
]
