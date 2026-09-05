from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='list'),
    path('<int:club_id>/', views.club_detail, name='detail'),
    path('<int:club_id>/ranking/<int:ranking_id>/', views.ranking_detail, name='ranking_detail'),
    path('<int:club_id>/torneio/<int:tournament_id>/', views.knockout_detail, name='knockout_detail'),
    path('<int:club_id>/torneio/<int:tournament_id>/categoria/<int:category_id>/', views.knockout_bracket, name='knockout_bracket'),
    path('download/modelo-torneio/', views.download_knockout_template, name='download_knockout_template'),
]
