from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress
from .models import SiteConfiguration, UserProfile, PlayerLinkRequest, ClubLead
from django.contrib.auth.forms import UserChangeForm, AdminUserCreationForm
from clubs.models import Club
from clubs.admin import ClubScopedAdminMixin

class CustomUserForm(UserChangeForm):
    managed_club = forms.ModelChoiceField(
        queryset=Club.objects.all(),
        required=False,
        label="Clube/Liga que irá administrar",
        empty_label="Nenhum"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            first_club = self.instance.managed_clubs.first()
            if first_club:
                self.initial['managed_club'] = first_club

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        if user.pk:
            club = self.cleaned_data.get('managed_club')
            if club:
                user.managed_clubs.set([club])
            else:
                user.managed_clubs.clear()
        return user

class CustomUserAddForm(AdminUserCreationForm):
    managed_club = forms.ModelChoiceField(
        queryset=Club.objects.all(),
        required=False,
        label="Clube/Liga que irá administrar",
        empty_label="Nenhum"
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        if user.pk:
            club = self.cleaned_data.get('managed_club')
            if club:
                user.managed_clubs.set([club])
            else:
                user.managed_clubs.clear()
        return user


admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    add_form = CustomUserAddForm
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Gestão de Clube/Liga', {'fields': ('managed_club',)}),
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser=False)
        return qs
        
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
                # Copiamos o dicionário para não alterar o original da classe
                new_opts = opts.copy()
                fields = new_opts.get('fields', ())
                
                # Se for a seção de permissões que contém is_superuser
                if 'is_superuser' in fields:
                    # Remove campos sensíveis, mantendo apenas is_active
                    new_opts['fields'] = tuple(f for f in fields if f in ['is_active'])
                
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

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    form = SiteConfigurationForm
    list_display = ['__str__', 'background_color', 'highlight_color']
    
    fieldsets = (
        ('Imagens / Vídeos / Marca d\'Água', {
            'fields': ('favicon', 'background_image', 'background_video', 'watermark_image', 'watermark_position', 'watermark_opacity', 'watermark_size_percent')
        }),
        ('Cores e Aparência', {
            'fields': ('background_color', 'overlay_color', 'overlay_opacity', 'highlight_color', 'title_color', 'subtitle_color')
        }),
        ('Rodapé (Footer)', {
            'fields': ('footer_show', 'footer_text', 'footer_width', 'footer_padding', 'footer_instagram', 'footer_facebook', 'footer_whatsapp')
        }),
        ('Monitoramento e SEO', {
            'fields': ('google_analytics_id',)
        }),
        ('Recursos e Exibição', {
            'fields': ('show_clubs_cta',)
        }),
    )
    
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
    list_display = ('club_name', 'name', 'phone', 'contacted', 'created_at')
    list_filter = ('contacted', 'created_at')
    search_fields = ('club_name', 'name', 'email', 'phone')
    list_editable = ('contacted',)
