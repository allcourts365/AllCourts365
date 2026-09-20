from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from clubs.models import Club, Court, Player, Match, Category, CategoryPlayer, Tournament, RankingTournament, KnockoutTournament, TournamentFee
from news.models import News, BroadcastMessage

class Command(BaseCommand):
    help = 'Cria o grupo Admin de Clube com as permissões corretas'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Administradores de Clubes')
        dept_group, dept_created = Group.objects.get_or_create(name='Administradores de Departamento')
        
        # Modelos que os admins (clube e departamento) podem gerenciar
        from clubs.models import Department
        models_to_manage = [Club, Department, Court, Player, Match, Category, CategoryPlayer, Tournament, RankingTournament, KnockoutTournament, TournamentFee, News, BroadcastMessage]
        
        permissions = []
        for model in models_to_manage:
            content_type = ContentType.objects.get_for_model(model)
            model_permissions = Permission.objects.filter(content_type=content_type)
            permissions.extend(model_permissions)
            
        # Adiciona Permissões especiais
        from core.models import PlayerLinkRequest, UserProfile
        from django.contrib.auth.models import User
        
        extra_models = [PlayerLinkRequest, UserProfile, User]
        for model in extra_models:
            ct = ContentType.objects.get_for_model(model)
            permissions.extend(Permission.objects.filter(content_type=ct))

        group.permissions.set(permissions)
        dept_group.permissions.set(permissions)
        
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Administradores de Clubes" criado com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS('Grupo "Administradores de Clubes" atualizado com sucesso!'))
            
        if dept_created:
            self.stdout.write(self.style.SUCCESS('Grupo "Administradores de Departamento" criado com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS('Grupo "Administradores de Departamento" atualizado com sucesso!'))
