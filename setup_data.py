import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allcourts365.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import SiteConfiguration
from clubs.models import Club, Tournament

# Criar Superusuário
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Superusuário 'admin' com senha 'admin' criado com sucesso.")

# Configurar Site
config, created = SiteConfiguration.objects.get_or_create(pk=1)
if created:
    config.background_color = '#0f172a'
    config.highlight_color = '#3b82f6'
    config.save()
    print("Configuração do Site inicializada.")

# Criar Clube de Teste
if not Club.objects.filter(name='TC22A').exists():
    club = Club.objects.create(name='TC22A', description='Clube de Tênis de Teste', address='Rua Exemplo, 123')
    print("Clube TC22A criado com sucesso.")
    
    # Criar um Torneio de Teste
    Tournament.objects.create(club=club, name='Ranking 2º Semestre', tournament_type='ranking')
    print("Torneio criado com sucesso.")
