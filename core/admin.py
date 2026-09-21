from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress
from .models import SiteConfiguration, FooterLink, UserProfile, PlayerLinkRequest, ClubLead, Message
from django.contrib.auth.forms import UserChangeForm, AdminUserCreationForm
from clubs.models import Club
from clubs.admin import ClubScopedAdminMixin
from ckeditor.widgets import CKEditorWidget

from django.contrib.auth.models import Group
from clubs.models import Department

ADMIN_TYPE_CHOICES = (
    ('', 'Nenhum'),
    ('clube', 'Administrador do Clube'),
    ('departamento', 'Administrador de Departamento'),
)

class BaseCustomUserForm(forms.ModelForm):
    is_staff = forms.BooleanField(
        required=False,
        label='Membro da Equipe (Acesso ao painel administrativo)'
    )
    admin_type = forms.ChoiceField(
        choices=ADMIN_TYPE_CHOICES,
        required=False,
        label="Tipo de Administrador"
    )
    managed_club = forms.ModelChoiceField(
        queryset=Club.objects.all(),
        required=False,
        label="Clube/Liga (Apenas Superusers)",
        empty_label="Nenhum"
    )
    managed_department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        required=False,
        label="Departamento",
        empty_label="-- Selecione um Departamento --"
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.initial['is_staff'] = self.instance.is_staff
            is_club_admin = self.instance.groups.filter(name='Administradores de Clubes').exists()
            is_dept_admin = self.instance.groups.filter(name='Administradores de Departamento').exists()
            
            if is_club_admin:
                self.initial['admin_type'] = 'clube'
            elif is_dept_admin:
                self.initial['admin_type'] = 'departamento'
                first_dept = self.instance.managed_departments.first()
                if first_dept:
                    self.initial['managed_department'] = first_dept
            
            first_club = self.instance.managed_clubs.first()
            if first_club:
                self.initial['managed_club'] = first_club

        if self.request:
            if self.request.user.is_superuser:
                self.fields['managed_department'].queryset = Department.objects.all()
            else:
                user_clubs = self.request.user.managed_clubs.all()
                self.fields['managed_department'].queryset = Department.objects.filter(club__in=user_clubs)

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'is_staff' in self.cleaned_data:
            user.is_staff = self.cleaned_data['is_staff']
            
        if commit:
            user.save()
        return user

class CustomUserForm(UserChangeForm, BaseCustomUserForm):
    pass

class CustomUserAddForm(AdminUserCreationForm, BaseCustomUserForm):
    pass

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    add_form = CustomUserAddForm
    
    def dynamic_get_clubs(self, obj):
        if hasattr(obj, 'annotated_club_name') and obj.annotated_club_name:
            return obj.annotated_club_name
        
        clubs = set()
        clubs.update(obj.managed_clubs.values_list('name', flat=True))
        return ", ".join(sorted(list(clubs))) if clubs else "-"
        
    dynamic_get_clubs.short_description = "Clube"
    dynamic_get_clubs.admin_order_field = 'annotated_club_name'

    def get_list_display(self, request):
        return ('username', 'email', 'first_name', 'last_name', 'is_staff', 'dynamic_get_clubs')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and obj:
            # ADM de departamento: pode editar usuarios mas NAO pode setar is_superuser nem is_staff
            if request.user.managed_departments.exists():
                return ('is_superuser', 'is_staff', 'groups', 'user_permissions', 'last_login', 'date_joined')
            # ADM de clube: pode setar is_staff e grupos via campos customizados, mas NAO is_superuser
            if request.user.managed_clubs.exists():
                return ('is_superuser', 'user_permissions', 'last_login', 'date_joined')
            # Outros staff sem clube/dept vinculado: restricao maxima
            return ('is_superuser', 'groups', 'user_permissions', 'is_staff', 'last_login', 'date_joined')
        return super().get_readonly_fields(request, obj)
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Controle de Acesso - Equipe', {
            'classes': ('wide',),
            'fields': ('is_staff', 'admin_type', 'managed_club', 'managed_department'),
        }),
    )
    
    class Media:
        js = ('admin/js/user_role_toggle.js',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        from django.db.models import F
        
        if request.user.is_superuser:
            return qs.annotate(annotated_club_name=F('player_profiles__club__name'))
            
        if not request.user.is_superuser:
            from django.db.models import Q
            user_clubs = request.user.managed_clubs.all()
            user_depts = request.user.managed_departments.all()
            qs = qs.annotate(annotated_club_name=F('player_profiles__club__name'))
            
            qs = qs.filter(
                Q(annotated_club_name__in=user_clubs.values_list('name', flat=True)) |
                Q(player_profiles__department__in=user_depts) |
                Q(player_profiles__club__departments__in=user_depts) |
                Q(managed_clubs__in=user_clubs) |
                Q(managed_departments__club__in=user_clubs) |
                Q(id=request.user.id)
            ).distinct()
            
            # ADM de departamento: só vê usuários normais (não-staff, não-superuser)
            if request.user.managed_departments.exists() and not request.user.managed_clubs.exists():
                qs = qs.filter(is_staff=False, is_superuser=False)
                
            return qs
        return qs
        
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        user = form.instance
        if not user.pk:
            return
        
        # Ler dados do form - is_staff pode vir como booleano do model ou do campo customizado
        # Na tela de criacao o campo is_staff vem do nosso BaseCustomUserForm
        # Na tela de edicao o campo is_staff do UserChangeForm pode sobrescrever
        admin_type = form.cleaned_data.get('admin_type', '')
        
        # Se nao ha admin_type definido, nao interferimos na atribuicao de grupos
        if not admin_type:
            return
            
        is_staff = form.cleaned_data.get('is_staff', user.is_staff)
        
        print(f'[save_related] user={user.username}, is_staff={is_staff}, admin_type={admin_type!r}')
        
        try:
            club_group = Group.objects.get(name='Administradores de Clubes')
            dept_group = Group.objects.get(name='Administradores de Departamento')
            
            # Remove dos grupos admin (manteremos outros grupos que possam existir)
            user.groups.remove(club_group, dept_group)
            user.managed_clubs.clear()
            user.managed_departments.clear()
            
            if is_staff:
                if admin_type == 'clube':
                    user.groups.add(club_group)
                    target_club = None
                    if request.user and not request.user.is_superuser:
                        target_club = request.user.managed_clubs.first()
                    else:
                        target_club = form.cleaned_data.get('managed_club')
                        
                    if target_club:
                        user.managed_clubs.add(target_club)
                    print(f'[save_related] Adicionado ao grupo Administradores de Clubes, clube={target_club}')
                        
                elif admin_type == 'departamento':
                    user.groups.add(dept_group)
                    target_dept = form.cleaned_data.get('managed_department')
                    if target_dept:
                        user.managed_departments.add(target_dept)
                    print(f'[save_related] Adicionado ao grupo Administradores de Departamento, dept={target_dept}')
        except Group.DoesNotExist as e:
            print(f'[save_related] ERRO: Grupo nao encontrado - {e}')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.email:
            email_address, created = EmailAddress.objects.get_or_create(
                user=obj,
                email=obj.email,
                defaults={'verified': True, 'primary': True}
            )
            if not created and not email_address.verified:
                email_address.verified = True
                email_address.save()
                
        if not change and not request.user.is_superuser:
            club = request.user.managed_clubs.first()
            dept = request.user.managed_departments.first()
            
            if dept:
                from clubs.models import Player
                Player.objects.get_or_create(
                    user=obj,
                    club=dept.club,
                    department=dept,
                    defaults={'name': obj.get_full_name() or obj.username}
                )
            elif club:
                from clubs.models import Player
                Player.objects.get_or_create(
                    user=obj,
                    club=club,
                    defaults={'name': obj.get_full_name() or obj.username}
                )

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)
        class FormWithRequest(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
        return FormWithRequest

    def get_fieldsets(self, request, obj=None):
        if not obj:
            fieldsets = list(self.add_fieldsets)
            if not request.user.is_superuser:
                fieldsets = [f for f in fieldsets if f[0] != 'Gestão de Clube/Liga']
            return fieldsets

        fieldsets = list(super(UserAdmin, self).get_fieldsets(request, obj))
        if request.user.is_superuser:
            fieldsets.append(('Gestão de Clube/Liga', {'fields': ('managed_club',)}))
            return fieldsets
        else:
            new_fieldsets = []
            for name, opts in fieldsets:
                new_opts = opts.copy()
                fields = new_opts.get('fields', ())
                
                if 'is_superuser' in fields:
                    if request.user.managed_clubs.exists():
                        new_opts['fields'] = tuple(f for f in fields if f in ['is_active', 'groups', 'is_staff'])
                    else:
                        new_opts['fields'] = tuple(f for f in fields if f in ['is_active'])
                
                if 'is_staff' in new_opts.get('fields', ()):
                    new_fields = ('is_staff', 'admin_type', 'managed_club', 'managed_department')
                    new_opts['fields'] = tuple(f for f in new_opts['fields'] if f not in new_fields) + new_fields
                    
                new_fieldsets.append((name, new_opts))
            return new_fieldsets

class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = '__all__'
        widgets = {
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'overlay_color': forms.TextInput(attrs={'type': 'color'}),
            'highlight_color': forms.TextInput(attrs={'type': 'color'}),
            'title_color': forms.TextInput(attrs={'type': 'color'}),
            'subtitle_color': forms.TextInput(attrs={'type': 'color'}),
        }

class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1
    fields = ('url', 'label', 'order')
    verbose_name = "Link do Rodapé"
    verbose_name_plural = "Links Dinâmicos do Rodapé"
    ordering = ('order',)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    form = SiteConfigurationForm
    list_display = ['__str__', 'background_color', 'highlight_color']
    inlines = [FooterLinkInline]
    change_form_template = 'admin/core/siteconfiguration/change_form.html'

    fieldsets = (
        ('Imagens / Vídeos / Marca d\'Água', {
            'fields': ('favicon', 'background_image', 'background_video', 'watermark_image', 'watermark_position', 'watermark_opacity', 'watermark_size_percent')
        }),
        ('Cores e Aparência', {
            'fields': ('background_color', 'overlay_color', 'overlay_opacity', 'highlight_color', 'title_color', 'subtitle_color')
        }),
        ('Rodapé (Footer)', {
            'description': '<div style="background:#e8f5e9;padding:10px;border-radius:6px;margin-bottom:10px;color:#1b5e20;font-size:13px;">'
                           '<strong>💡 Links Dinâmicos:</strong> Adicione os links do rodapé na tabela abaixo desta seção. '
                           'O ícone é detectado automaticamente pela URL (Instagram, Facebook, WhatsApp, YouTube, etc.).</div>',
            'fields': ('footer_show', 'footer_text', 'footer_width', 'footer_padding')
        }),
        ('Monitoramento e SEO', {
            'fields': ('google_analytics_id',)
        }),
        ('Recursos e Exibição', {
            'fields': ('show_clubs_cta', 'club_cta_title', 'club_cta_text', 'club_cta_whatsapp')
        }),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(UserProfile)
class UserProfileAdmin(ClubScopedAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'racket', 'handedness', 'backhand')
    search_fields = ('user__username', 'user__email', 'full_name', 'phone', 'city')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'full_name', 'phone', 'birth_date', 'city', 'shirt_size')
        }),
        ('Ficha Técnica (Tênis)', {
            'fields': ('racket', 'handedness', 'backhand', 'string_tension', 'string_type', 'play_style', 'best_shot', 'tennis_idol', 'preferred_time')
        }),
        ('Mídia', {
            'fields': ('avatar',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            from django.db.models import Q
            return qs.filter(
                Q(user__player_profiles__club__administrators=request.user) |
                Q(user__player_profiles__club__departments__administrators=request.user) |
                Q(user__managed_clubs__administrators=request.user) |
                Q(user_id=request.user.id)
            ).distinct()
        return qs

@admin.register(PlayerLinkRequest)
class PlayerLinkRequestAdmin(ClubScopedAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'club', 'player', 'status', 'created_at')
    list_filter = ('status', ('club', admin.RelatedOnlyFieldListFilter))
    search_fields = ('user__username', 'user__email', 'player__name')
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description='Aprovar solicitações selecionadas')
    def approve_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.status = 'approved'
            req.save()
            # Efetua o vínculo
            req.player.user = req.user
            req.player.save()
        self.message_user(request, "Solicitações aprovadas e usuários vinculados aos atletas com sucesso.")

    @admin.action(description='Rejeitar solicitações selecionadas')
    def reject_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.status = 'rejected'
            req.save()
        self.message_user(request, "Solicitações rejeitadas e vínculos desfeitos (se aplicável).")

@admin.register(ClubLead)
class ClubLeadAdmin(admin.ModelAdmin):
    list_display = ('club_name', 'status_novo', 'name', 'phone', 'contacted', 'created_at')
    list_filter = ('contacted', 'created_at')
    search_fields = ('club_name', 'name', 'email', 'phone')
    list_editable = ('contacted',)

    @admin.display(description='', ordering='contacted')
    def status_novo(self, obj):
        from django.utils.safestring import mark_safe
        if not obj.contacted:
            return mark_safe(
                '<span style="background:#ef4444;color:#fff;padding:2px 8px;'
                'border-radius:10px;font-size:0.72rem;font-weight:700;'
                'letter-spacing:0.5px;">NOVO</span>'
            )
        return ''
