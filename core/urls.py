from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout-redirect/', views.logout_and_redirect, name='logout_redirect'),
    path('redirecionar/', views.login_redirect, name='login_redirect'),
    path('painel-atleta/', views.athlete_dashboard, name='athlete_dashboard'),
    path('meus-jogos/', views.my_games_calendar, name='my_games_calendar'),
    path('api/meus-jogos/', views.api_my_games, name='api_my_games'),
    path('api/agenda/', views.api_court_agenda, name='api_court_agenda'),
    path('api/agenda/mensal/', views.api_monthly_agenda, name='api_monthly_agenda'),
    path('para-clubes/', views.club_landing_page, name='club_landing_page'),
]
