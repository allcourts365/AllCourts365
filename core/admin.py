from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import SiteConfiguration, UserProfile, PlayerLinkRequest

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser=False)
        return qs

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            new_fieldsets = []
            for name, opts in fieldsets:
                # Copiamos o dicionário para não alterar o original da classe
                new_opts = opts.copy()
                fields = new_opts.get('fields', ())
                
                # Se for a seção de permissões que contém is_superuser
                if 'is_superuser' in fields:
                    # Remove campos sensíveis, mantendo apenas is_active
                    new_opts['fields'] = tuple(f for f in fields if f in ['is_active'])
                
                new_fieldsets.append((name, new_opts))
            return new_fieldsets
        return fieldsets

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

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    form = SiteConfigurationForm
    list_display = ['__str__', 'background_color', 'highlight_color']
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'racket', 'handedness', 'backhand')
    search_fields = ('user__username', 'user__email', 'full_name')

@admin.register(PlayerLinkRequest)
class PlayerLinkRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'player', 'status', 'created_at')
    list_filter = ('status', 'club')
    search_fields = ('user__username', 'user__email', 'player__name')
    actions = ['approve_requests', 'reject_requests']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(club__administrators=request.user)

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
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, "Solicitações rejeitadas.")
