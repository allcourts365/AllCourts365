from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

@login_required
def login_redirect(request):
    user = request.user
    
    # 1. Se for superuser, staff, ou administrador de algum clube, vai pro Admin em nova aba
    if user.is_staff or user.is_superuser or user.managed_clubs.exists():
        return render(request, 'admin_redirect.html')
        
    # 2. Se for um atleta, vai pro painel do atleta
    if hasattr(user, 'player_profile'):
        return redirect('athlete_dashboard')
        
    # 3. Fallback (se logar mas não for nenhum dos dois, manda pra home)
    return redirect('home')

@login_required
def athlete_dashboard(request):
    # Por enquanto, renderiza apenas um placeholder
    return render(request, 'athlete_dashboard.html')
