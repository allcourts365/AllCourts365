from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='list'),
    path('<int:club_id>/', views.club_detail, name='detail'),
    path('<int:club_id>/ranking/<int:ranking_id>/', views.ranking_detail, name='ranking_detail'),
]
