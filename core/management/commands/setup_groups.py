from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from clubs.models import Club, Court, Player, Match, Category, Registration
from news.models import News

class Command(BaseCommand):
    help = 'Cria o grupo Admin de Clube com as permissões corretas'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Admin de Clube')
        
        # Modelos que o admin do clube pode gerenciar
        models_to_manage = [Club, Court, Player, Match, Category, Registration, News]
        
        permissions = []
        for model in models_to_manage:
            content_type = ContentType.objects.get_for_model(model)
            model_permissions = Permission.objects.filter(content_type=content_type)
            permissions.extend(model_permissions)
            
        # Adiciona Permissões especiais do app CORE se precisar (ex: PlayerLinkRequest)
        from core.models import PlayerLinkRequest
        ct_link = ContentType.objects.get_for_model(PlayerLinkRequest)
        permissions.extend(Permission.objects.filter(content_type=ct_link))

        group.permissions.set(permissions)
        
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Admin de Clube" criado com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS('Grupo "Admin de Clube" atualizado com sucesso!'))
