from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='list'),
    path('<int:club_id>/', views.club_detail, name='detail'),
]
