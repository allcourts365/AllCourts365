from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Cria/atualiza os grupos de ADM com as permissões corretas'

    def handle(self, *args, **kwargs):
        self.setup_club_admin_group()
        self.setup_dept_admin_group()

    def setup_club_admin_group(self):
        group, created = Group.objects.get_or_create(name='Administradores de Clubes')

        # ADM de Clube: pode tudo referente ao clube, menos criar superusers
        # (is_superuser fica bloqueado via readonly_fields no admin)
        # NAO pode ver: SiteConfiguration, FooterLink, ClubLead (so superuser)
        allowed = [
            ('clubs', 'category'),
            ('clubs', 'categoryplayer'),
            ('clubs', 'club'),
            ('clubs', 'court'),
            ('clubs', 'department'),
            ('clubs', 'knockouttournament'),
            ('clubs', 'match'),
            ('clubs', 'player'),
            ('clubs', 'rankingtournament'),
            ('clubs', 'tournament'),
            ('clubs', 'tournamentfee'),
            ('core', 'broadcastmessage'),
            ('core', 'message'),
            ('core', 'playerlinkrequest'),
            ('core', 'userprofile'),
            ('news', 'broadcastmessage'),
            ('news', 'news'),
            ('auth', 'user'),   # pode criar/editar usuarios (sem poder setar is_superuser)
        ]

        perms = self._get_perms(allowed)
        group.permissions.set(perms)

        verb = 'criado' if created else 'atualizado'
        self.stdout.write(self.style.SUCCESS(
            f'Grupo "Administradores de Clubes" {verb} com {perms.count()} permissoes.'
        ))

    def setup_dept_admin_group(self):
        group, created = Group.objects.get_or_create(name='Administradores de Departamento')

        # ADM de Departamento: pode gerenciar tudo do departamento/clube
        # NAO pode: criar superuser, criar staff, ver SiteConfiguration/ClubLead/FooterLink
        allowed = [
            ('clubs', 'category'),
            ('clubs', 'categoryplayer'),
            ('clubs', 'court'),
            ('clubs', 'knockouttournament'),
            ('clubs', 'match'),
            ('clubs', 'player'),
            ('clubs', 'rankingtournament'),
            ('clubs', 'tournament'),
            ('clubs', 'tournamentfee'),
            ('clubs', 'department'),
            ('clubs', 'club'),
            ('core', 'broadcastmessage'),
            ('core', 'message'),
            ('core', 'playerlinkrequest'),
            ('core', 'userprofile'),
            ('news', 'broadcastmessage'),
            ('news', 'news'),
            # view e change de user (somente usuarios normais - filtrado pelo get_queryset)
            # SEM add_user - ADM de dept NAO cria staff/superusers
        ]

        # Permissoes especificas de view+change para auth.user
        perms = self._get_perms(allowed)
        try:
            from django.contrib.contenttypes.models import ContentType
            ct = ContentType.objects.get(app_label='auth', model='user')
            user_view_change = Permission.objects.filter(content_type=ct, codename__in=['view_user', 'change_user'])
            perms = perms | user_view_change
        except ContentType.DoesNotExist:
            pass
        group.permissions.set(perms)

        verb = 'criado' if created else 'atualizado'
        self.stdout.write(self.style.SUCCESS(
            f'Grupo "Administradores de Departamento" {verb} com {perms.count()} permissoes.'
        ))

    def _get_perms(self, allowed_list):
        perms = Permission.objects.none()
        for app_label, model in allowed_list:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                perms = perms | Permission.objects.filter(content_type=ct)
            except ContentType.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'  AVISO: {app_label}.{model} nao encontrado, pulando...'
                ))
        return perms
