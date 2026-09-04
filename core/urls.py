from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('redirecionar/', views.login_redirect, name='login_redirect'),
    path('painel-atleta/', views.athlete_dashboard, name='athlete_dashboard'),
    path('api/agenda/', views.api_court_agenda, name='api_court_agenda'),
    path('api/agenda/mensal/', views.api_monthly_agenda, name='api_monthly_agenda'),
]
